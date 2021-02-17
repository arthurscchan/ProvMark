#!/usr/bin/env python3

import os
import sys
import time
import shutil
import subprocess
import configparser

#Print help menu
def helpMenu(name):
	print ('Usage: %s <Generalized Graph (Version 1)> <Generalized Graph (Version 2)>' % name)
        print ('Generalized Graph: Generalized graph for comparison')

#Prepare stage and working directory
def prepareDir(directory):
	if os.path.exists(directory):
		subprocess.call(['sudo','rm','-rf',directory])
	os.makedirs(directory)
	os.chown(directory,1000,1000)

#Check Arguments
if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]) or not os.path.isfile(sys.argv[2]):
	helpMenu(sys.argv[0])
	quit()

baseDir = os.path.abspath('%s/../' % os.path.dirname(sys.argv[0]))
v1Graph = os.path.abspath(sys.argv[1])
v2Graph = os.path.abspath(sys.argv[2])
workingDir = os.path.abspath('%s/working/' % baseDir)
outDir = os.path.abspath('%s/result/' % baseDir)

prepareDir(workingDir)
prepareDir(outDir)

#Compare and generate benchmark
print ('Start comparing graphs')

os.system('sudo chmod +x %s/processGraph/findSubgraph.py' % baseDir)

#Version 1 as background
command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 %s %s %s/resultv1v2.clingo
''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), v1Graph, v2Graph, outDir)
subprocess.call(command.split())

#Version 2 as background
command = '''sudo %s/processGraph/findSubgraph.py %s %s 1 %s %s %s/resultv2v1.clingo
''' % (baseDir, workingDir, ('%s/processGraph/template.lp' % baseDir), v2Graph, v1Graph, outDir)
subprocess.call(command.split())
		
print ('End of comparing graphs\n')

