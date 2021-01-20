#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Tools> <Tools Base Directory (Version 1)> <Tools Base Direrctory (Version2)> <Benchmark Program Directory>' % name)
	print ('Tools:\n\tspg:\tSPADE with Graphviz storage\n\tspn:\tSPADE with Neo4j storage\n\topu:\tOPUS\n\tcam:\tCamFlow')
	print ('Tools Base Directory: Base directory of the chosen tools and version')
	print ('Benchmark Program Directory: Base directory of the benchmark program')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)
	os.chown(directory,1000,1000)

#Check Arguments
if len(sys.argv) != 4:
	helpMenu(sys.argv[0])
	quit()

trial = 20
round = 1
baseDir = os.path.abspath('%s/../' % os.path.dirname(sys.argv[0]))
tool = sys.argv[1]
v1ToolBaseDir = os.path.abspath(sys.argv[2])
v2ToolBaseDir = os.path.abspath(sys.argv[3])
benchmarkDir = os.path.abspath(sys.argv[4])
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
filterGraphs = config.getboolean(tool, 'filtergraphs')

#Stage 1 - Start the tools and generate graph (neo4j / dot / provjson)
start = time.time()
print ('Starting stage 1...Generating provenance from native tools')

os.system('sudo chmod +x %s/startTool/%s' % (baseDir, stage1Tool.split()[0]))
stage1Command = 'sudo %s/startTool/%s %s %s %s %s %s' % (baseDir, stage1Tool, stageDir, workingDir, 'test' , '%s' , '%s')

print ('Version 1')
for i in range(1,trial+1):
	subprocess.check_output(('%s/prepare %s --static -DPROGRAM -DREAD=2 -DWRITE=2 -DROUND=%d' %(benchmarkDir,stageDir,round)).split())
	v1Fingerprint = subprocess.check_output((stage1Command % (v1ToolBaseDir, 'version1-%d' % i)).split()).decode().split()
print ('End version 1')

print ('Version 2')
for i in range(1,trial+1):
	subprocess.check_output(('%s/prepare %s --static -DPROGRAM -DREAD=2 -DWRITE=2 -DROUND=%d' %(benchmarkDir,stageDir,round)).split())
	v2Fingerprint = subprocess.check_output((stage1Command % (v2ToolBaseDir, 'version2-%d' % i)).split()).decode().split()
print ('End version 2')


print ('End of stage 1\n')
end = time.time()
t1 = end-start

#Stage 2 - Transform to Clingo graph
start = time.time()
print ('Starting stage 2...Transforming provenance result to Clingo graph')

os.system('sudo chmod +x %s/genClingoGraph/%s' % (baseDir, stage2Handler.split()[0]))
stage2Command = 'sudo %s/genClingoGraph/%s %s %s %s' % (baseDir, stage2Handler, '%s', '%s', '%s')

for fingerprint in v1Fingerprint:
	dir = os.path.abspath('%s/version1-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		i = 1
		for file in os.listdir(dir):
			suffix = 'version1-%d' % i
			subprocess.call((stage2Command % (suffix, file, dir)).split())
			i += 1

for fingerprint in v2Fingerprint:
	dir = os.path.abspath('%s/version2-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		i = 1
		for file in os.listdir(dir):
			suffix = 'version2-%d' % i
			subprocess.call((stage2Command % (suffix,file,dir)).split())
			i += 1

print ('End of stage 2\n')
end = time.time()
t2 = end-start

if filterGraphs:
	#Stage 3a - Filter out non-isomorphic graphs
	start = time.time()
	print ('Starting stage 3a...Filtering out non-isomorphic graphs')

	os.system('sudo chmod +x %s/processGraph/filterGraphs.py' % baseDir)
	stage3aCommand = 'sudo %s/processGraph/filterGraphs.py %s %s %s' % (baseDir,workingDir, ('%s/processGraph/isoTemplate.lp' % baseDir), '%s')

	for fingerprint in v1Fingerprint:
		dir = os.path.abspath('%s/version1-%s' % (workingDir, fingerprint))
		if os.path.isdir(dir):
			command = stage3aCommand
			for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-version1')):
				command = command % ('%s %s' % (file, '%s'))
			subprocess.call((command % '').split())

	for fingerprint in v2Fingerprint:
		dir = os.path.abspath('%s/version2-%s' % (workingDir, fingerprint))
		if os.path.isdir(dir):
			command = stage3aCommand
			for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-version2')):
				command = command % ('%s %s' % (file, '%s'))
			subprocess.call((command % '').split())

	print ('End of stage 3a\n')
	end = time.time()
	t3a= end-start

#Stage 3 - Generalize graph
start = time.time()
print ('Starting stage 3...Generalizing graph from multiple trial')

os.system('sudo chmod +x %s/processGraph/generalizeGraph.py' % baseDir)
stage3Command = 'sudo %s/processGraph/generalizeGraph.py %s %s %s' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), '%s')

for fingerprint in v1Fingerprint:
	dir = os.path.abspath('%s/version1-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		command = stage3Command % ('version1-%s %s' % (fingerprint, '%s'))
		for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-version1')):
			command = command % ('%s %s' % (file, '%s'))
		subprocess.call((command % '').split())

for fingerprint in v2Fingerprint:
	dir = os.path.abspath('%s/program-%s' % (workingDir, fingerprint))
	if os.path.isdir(dir):
		command = stage3Command % ('version2-%s %s' % (fingerprint, '%s'))
		for file in ('%s/%s' % (dir,name) for name in os.listdir(dir) if name.startswith('clingo-version2')):
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
for fingerprint in v1Fingerprint:
	if fingerprint in v2Fingerprint:
		#Version 1 as background
		stage4Command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 general.clingo-version1-%s general.clingo-version2-%s %s
        	''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), fingerprint, fingerprint, ('''%s/resultv1v2-%s.clingo
        	''' % (outDir,fingerprint)))
		subprocess.call(stage4Command.split())
		
		#Version 2 as background	
		stage4Command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 general.clingo-version2-%s general.clingo-version1-%s %s
        	''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), fingerprint, fingerprint, ('''%s/resultv2v1-%s.clingo
        	''' % (outDir,fingerprint)))
		subprocess.call(stage4Command.split())


print ('End of stage 4\n')
end = time.time()
t4 = end-start

with open('/tmp/time.log', 'a') as file:
	file.write("%s, %s, %.3f, %.3f, %.3f, %.3f\n" % (tool, os.path.basename(benchmarkDir).lower()[3:], t1, t2, t3, t4))

