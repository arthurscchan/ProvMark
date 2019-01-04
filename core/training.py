#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Tools> <Tools Base Directory> <Benchmark Program Directory> [<Trial>]' % name)
	print ('Tools:\n\tspg:\tSPADE with Graphviz storage\n\tspn:\tSPADE with Neo4j storage\n\topu:\tOPUS\n\tcam:\tCamFlow')
	print ('Tools Base Directory: Base directory of the chosen tools (type . if tools are globally accessible)')
	print ('Benchmark Program Directory: Base directory of the benchmark program')
	print ('Trial:	Number of trial provenance capture for each case (Default: 2)')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)
	os.chown(directory,1000,1000)

#Check Arguments
trial = 2
if len(sys.argv) < 4 or len(sys.argv) > 5:
	helpMenu(sys.argv[0])
	quit()
elif len(sys.argv) == 5:
	trial = int(sys.argv[4])

if trial < 2:
	trial = 2
baseDir = os.path.abspath('%s/../' % os.path.dirname(sys.argv[0]))
tool = sys.argv[1]
toolBaseDir = os.path.abspath(sys.argv[2])
benchmarkDir = os.path.abspath(sys.argv[3])
stageDir = os.path.abspath('%s/stage/' % baseDir)
workingDir = os.path.abspath('%s/working/' % baseDir)
outDir = os.path.abspath('%s/result/' % baseDir)

prepareDir(stageDir)
prepareDir(workingDir)
prepareDir(outDir)

#Parse Config File
config = configparser.ConfigParser()
config.read('%s/config/config.ini' % baseDir)

stage1Tool = config[tool]['stage1tool']
stage2Handler = config[tool]['stage2handler']

#Stage 1 - Start the tools and generate graph (neo4j / dot / provjson)
start = time.time()
print ('Starting stage 1...Generating provenance from native tools')

os.system('sudo chmod +x %s/startTool/%s' % (baseDir, stage1Tool.split()[0]))
stage1Command = 'sudo %s/startTool/%s %s %s %s %s %s' % (baseDir, stage1Tool, stageDir, workingDir, 'test' , toolBaseDir , '%s')

print ('Program')
for i in range(1,trial+1):
#	subprocess.check_output(('%s/prepare %s --static -DPROGRAM -DRANDOM -DREAD=2 -DWRITE=2' %(benchmarkDir,stageDir)).split())
	subprocess.check_output(('%s/prepare %s --static -DPROGRAM -DREAD=2 -DWRITE=2' %(benchmarkDir,stageDir)).split())
	programFingerprint = subprocess.check_output((stage1Command % ('program-%d' % i)).split()).decode().split()
print ('End Program')

print ('Control')
for i in range(1,trial+1):
#	subprocess.check_output(('%s/prepare %s --static -DCONTROL -DRANDOM -DREAD=2 -DWRITE=2' %(benchmarkDir,stageDir)).split())
	subprocess.check_output(('%s/prepare %s --static -DCONTROL -DREAD=2 -DWRITE=2' %(benchmarkDir,stageDir)).split())
	controlFingerprint = subprocess.check_output((stage1Command % ('control-%d' % i)).split()).decode().split()
print ('End Control')

print ('End of stage 1\n')
end = time.time()
t1 = end-start

#Stage 2 - Transform to Clingo graph
start = time.time()
print ('Starting stage 2...Transforming provenance result to Clingo graph')

os.system('sudo chmod +x %s/genClingoGraph/%s' % (baseDir, stage2Handler.split()[0]))
stage2Command = 'sudo %s/genClingoGraph/%s %s %s %s' % (baseDir, stage2Handler, '%s', '%s', '%s')

for fingerprint in controlFingerprint:
	dir = os.path.abspath('%s/control-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		i = 1
		for file in os.listdir(dir):
			suffix = 'control-%d' % i
			subprocess.call((stage2Command % (suffix,file,dir)).split())
			i += 1

for fingerprint in programFingerprint:
	dir = os.path.abspath('%s/program-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		i = 1
		for file in os.listdir(dir):
			suffix = 'program-%d' % i
			subprocess.call((stage2Command % (suffix,file,dir)).split())
			i += 1

print ('End of stage 2\n')
end = time.time()
t2 = end-start

#Stage 3 - Generalize graph
start = time.time()
print ('Starting stage 3...Generalizing graph from multiple trial')

os.system('sudo chmod +x %s/processGraph/generalizeGraph.py' % baseDir)
stage3Command = 'sudo %s/processGraph/generalizeGraph.py %s %s %s' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), '%s')

for fingerprint in controlFingerprint:
	dir = os.path.abspath('%s/control-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		command = stage3Command % ('control-%s %s' % (fingerprint, '%s'))
		for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-control')):
			command = command % ('%s %s' % (file, '%s'))
		subprocess.call((command % '').split())

for fingerprint in programFingerprint:
	dir = os.path.abspath('%s/program-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		command = stage3Command % ('program-%s %s' % (fingerprint, '%s'))
		for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-program')):
			command = command % ('%s %s' % (file, '%s'))
		subprocess.call((command % '').split())

print ('End of stage 3\n')
end = time.time()
t3 = end-start

for file in (file for file in os.listdir(workingDir) if file.startswith('general.clingo')):
	shutil.copyfile('%s/%s' % (workingDir,file), '%s/%s' % (outDir,file))

#Stage 4 - Compare and generate benchmark
start = time.time()
print ('Starting stage 4...Generating benchmark')

os.system('sudo chmod +x %s/processGraph/findSubgraph.py' % baseDir)
for fingerprint in programFingerprint:
	if len(controlFingerprint) > 1:
		editDistance = sys.maxsize 
		for backgroundFingerprint in controlFingerprint:
			preStage4Command = '''sudo %s/processGraph/calEditDistance.py %s %s/general.clingo-control-%s 
			%s/general.clingo-program-%s''' % (baseDir, ('''%s/processGraph/editdist.lp
			''' % baseDir), workingDir, backgroundFingerprint, workingDir, fingerprint)
			newEditDistance = int(subprocess.check_output(preStage4Command.split()))
			if newEditDistance < editDistance:
				editDistance = newEditDistance
				background = backgroundFingerprint
	else:
		background = controlFingerprint[0]	
	
	stage4Command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 general.clingo-control-%s general.clingo-program-%s %s
        ''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), background, fingerprint, ('''%s/result-%s.clingo
        ''' % (outDir,fingerprint)))
	subprocess.call(stage4Command.split())

print ('End of stage 4\n')
end = time.time()
t4 = end-start

with open('/tmp/time.log', 'a') as file:
	file.write("%s, %s, %.3f, %.3f, %.3f, %.3f\n" % (tool, os.path.basename(benchmarkDir).lower()[3:], t1, t2, t3, t4))

