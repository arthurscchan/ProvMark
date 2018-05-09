#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Tools> <Tools Base Directory> <Benchmark Directory> [<Trial>]' % name)
	print ('Tools:\n\tspg:\tSPADE with Graphviz storage\n\tspn:\tSPADE with Neo4j storage\n\topu:\tOPUS\n\tcam:\tCamFlow')
	print ('Tools Base Directory: Base directory of the chosen tool')
	print ('Benchmark Directory: Base directory of the benchmark program')
	print ('Trial:	Number of trial executed for each graph for generalization (Default: 2)')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)

#Check Arguments
trial = 2
outFile = os.path.abspath('./result.clingo')
if len(sys.argv) < 4 or len(sys.argv) > 5:
	helpMenu(sys.argv[0])
	quit()
elif len(sys.argv) == 5:
	trial = int(sys.argv[4])

if trial < 2:
	trial = 2
baseDir = os.path.abspath(os.path.dirname(sys.argv[0]))
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
template = config[tool]['template']

#Stage 1 - Start the tools and generate graph (neo4j / dot / provjson)
start = time.time()
print ('Starting stage 1...Generating provenance from native tools')

os.system('sudo chmod +x %s/startTool/%s' % (baseDir, stage1Tool.split()[0]))
stage1Command = 'sudo %s/startTool/%s %s %s %s %s %s %s %d' % (baseDir, stage1Tool, stageDir, workingDir, '%s' , '%s', toolBaseDir , '%s', trial)
print ('Program')
subprocess.call((stage1Command % (benchmarkDir, '-DPROGRAM', 'program')).split())
print ('End Program')
print ('Control')
subprocess.call((stage1Command % (benchmarkDir, '-DCONTROL', 'control')).split())
print ('End Control')

print ('End of stage 1\n')
end = time.time()
t1 = end-start

#Stage 2 - Transform to Clingo graph
start = time.time()
print ('Starting stage 2...Transforming provenance result to Clingo graph')

os.system('sudo chmod +x %s/genClingoGraph/%s' % (baseDir, stage2Handler.split()[0]))
stage2Command = 'sudo %s/genClingoGraph/%s %s %s %s' % (baseDir, stage2Handler, '%s', template, workingDir)
for i in range(1,trial+1):
	suffix = 'control-%d' % i
	subprocess.call((stage2Command % (suffix,suffix)).split())
for i in range(1,trial+1):
	suffix = 'program-%d' % i
	subprocess.call((stage2Command % (suffix,suffix)).split())
print ('End of stage 2\n')
end = time.time()
t2 = end-start

#Stage 3 - Generalize graph
start = time.time()
print ('Starting stage 3...Generalizing graph from multiple trial')

os.system('sudo chmod +x %s/processGraph/generalizeGraph.py' % baseDir)
stage3Command = 'sudo %s/processGraph/generalizeGraph.py %s %s %s' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), '%s')

command = stage3Command % ('control %s')
for i in range(1,trial+1):
	suffix = 'control-%d' % i
	command = command % ('%s/clingo-%s %s' % (workingDir, suffix, '%s'))
subprocess.call((command % ' ').split())

command = stage3Command % ('program %s')
for i in range(1,trial+1):
	suffix = 'program-%d' % i
	command = command % ('%s/clingo-%s %s' % (workingDir, suffix,'%s'))
subprocess.call((command % '').split())

print ('End of stage 3\n')
end = time.time()
t3 = end-start

shutil.copyfile('%s/general.clingo-program' % workingDir, '%s/general.clingo-program' % outDir)
shutil.copyfile('%s/general.clingo-control' % workingDir, '%s/general.clingo-control' % outDir)

#Stage 4 - Compare and generate benchmark
start = time.time()
print ('Starting stage 4...Generating benchmark')

os.system('sudo chmod +x %s/processGraph/findSubgraph.py' % baseDir)
stage4Command = 'sudo %s/processGraph/findSubgraph.py %s %s 1 general.clingo-control general.clingo-program %s' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), ('%s/result.clingo' % outDir))
subprocess.call(stage4Command.split())

print ('End of stage 4\n')
end = time.time()
t4 = end-start

with open('%s/time.log' % workingDir, 'a') as file:
	file.write("%s, %s, %.3f, %.3f, %.3f, %.3f\n" % (tool, os.path.basename(benchmarkDir).lower()[3:], t1, t2, t3, t4))

