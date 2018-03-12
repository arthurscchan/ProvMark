#!/usr/bin/env python3

import os
import sys
import time
import subprocess

#Retrieve arguments
trial = 0
if len(sys.argv) == 8:
	if sys.argv[7].isdigit():
		trial = int(sys.argv[7])
elif len(sys.argv) != 7:	
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Directory> <GCC Marco> <OPUS Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progPath = os.path.abspath(sys.argv[3])
gccMacro = sys.argv[4]
opusPath = os.path.abspath(sys.argv[5])
suffix = sys.argv[6]

#Prepare OPUS wrapper
os.chdir(opusPath)
subprocess.call('./update-wrapper')

os.chdir(workingPath)

#Get Audit Log
for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s %s' % (progPath,stagePath,gccMacro)).split())

	#Config OPUS Server
	pipe = subprocess.Popen(['%s/bin/opusctl' % opusPath, 'conf'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

	#Choose a location for the OPUS master config
	config = '%s/.opus-cfg\n' % workingPath
	#Where is your OPUS installation?
	config = '%s%s/\n' % (config,opusPath)
	#Choose an address for provenance data collection.
	config = '%s\n' % config
	#Choose a location for the OPUS database to reside in
	config = '%s%s/output.db-%s-%d\n' % (config,workingPath,suffix,i)
	#Choose a location for the OPUS bash variables cfg_file
	config = '%s%s/.opus-vars\n' % (config,workingPath)
	#What is the location of your python 2.7 binary?
	config = '%s\n' % config
	#Where is your jvm installation?
	config = '%s/usr/lib/jvm/java-8-oracle\n' % config
	#Address to use for provenance server communications.
	config = '%s\n' % config
	#Set OPUS to debug mode
	config = '%sFalse\n' % config

	pipe.communicate(input=config.encode())

	baseCommand = '%s/bin/opusctl --conf %s/.opus-cfg %s' % (opusPath,workingPath,'%s')
	#Start Opus Server
	subprocess.call((baseCommand % 'server start').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Capture Provenance
	subprocess.call((baseCommand % ('process launch %s/test' % stagePath)).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	
	#Stop Opus Server
	subprocess.call((baseCommand % 'server stop').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Wait for Data Flushing
	time.sleep(2)
