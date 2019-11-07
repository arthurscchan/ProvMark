#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Tools> <Tools Base Directory> <Benign Audit Log> <Target Audit Log>' % name)
	print ('Tools:\n\tspg:\tSPADE with Graphviz storage\n\tspn:\tSPADE with Neo4j storage')
	print ('Tools Base Directory: Base directory of the chosen tools (type . if tools are globally accessible)')
	print ('Benign Audit Log: Path for the benign audit log file')
	print ('Target Audit Log: Path for the target audit log file for integrity checking')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)
	os.chown(directory,1000,1000)

#Check Arguments
if len(sys.argv) != 5:
	helpMenu(sys.argv[0])
	quit()

baseDir = os.path.abspath('%s/../' % os.path.dirname(sys.argv[0]))
tool = sys.argv[1]
toolBaseDir = os.path.abspath(sys.argv[2])
benignAuditLog = os.path.abspath(sys.argv[3])
targetAuditLog = os.path.abspath(sys.argv[4])
workingDir = os.path.abspath('%s/working/' % baseDir)
outDir = os.path.abspath('%s/result/' % baseDir)

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
stage1Command = 'sudo %s/startTool/%s%s . %s . %s %s' % (baseDir, stage1Tool, 's', workingDir, toolBaseDir , '%s')

#Copy audit log file to correct location
try:
	shutil.copyfile(benignAuditLog, '%s/benign-input.log' % workingDir)
	shutil.copyfile(targetAuditLog, '%s/target-input.log' % workingDir)
except:
	pass

print ('Benign Audit Log')
print (stage1Command % 'benign')
subprocess.check_output((stage1Command % 'benign').split())
print ('End Benign Audit Log')

print ('Target Audit Log')
subprocess.check_output((stage1Command % 'target').split())
print ('End Target Audit Log')

print ('End of stage 1\n')
end = time.time()
t1 = end-start
quit()
#Stage 2 - Transform to Clingo graph
start = time.time()
print ('Starting stage 2...Transforming provenance result to Clingo graph')

os.system('sudo chmod +x %s/genClingoGraph/%s' % (baseDir, stage2Handler.split()[0]))
stage2Command = 'sudo %s/genClingoGraph/%s %s %s %s' % (baseDir, stage2Handler, '%s', '%s', workingDir)

for file in os.listdir(workingDir):
	subprocess.call((stage2Command % (file.split('-')[1],file)).split())

print ('End of stage 2\n')
end = time.time()
t2 = end-start

#Stage 3 - Generalize graph
#Skipping Generailzation
#Assumed generalied graph: clingo-benign / clingo-target

#Stage 4 - Compare and generate benchmark
start = time.time()
print ('Starting stage 4...Generating benchmark')

os.system('sudo chmod +x %s/processGraph/findSubgraph.py' % baseDir)

stage4Command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 clingo-target cling-benign %s
        ''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), ('''%s/result.clingo''' % outDir))

subprocess.call(stage4Command.split())

print ('End of stage 4\n')
end = time.time()
t4 = end-start

with open('/tmp/time.log', 'a') as file:
	file.write("%s, %s, %.3f, %.3f, %.3f, %.3f\n" % ('%s%s' % (tool,'(static)'), os.path.basename(benchmarkDir).lower()[3:], t1, t2, t3, t4))

