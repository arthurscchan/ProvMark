#!/usr/bin/env python3

import os
import sys
import time
import subprocess

#Retrieve arguments
trial = 0
if len(sys.argv) == 7:
	if sys.argv[6].isdigit():
		trial = int(sys.argv[6])
elif len(sys.argv) != 6:	
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Directory> <OPUS Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progPath = os.path.abspath(sys.argv[3])
opusPath = os.path.abspath(sys.argv[4])
suffix = sys.argv[5]

#Get Audit Log
for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s' % (progPath,stagePath)).split())

	#Config OPUS Server
	pipe = subprocess.Popen(['%s/bin/opusctl' % opusPath, 'conf'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

	#Choose a location for the OPUS master config
	input = '%s/.opus-cfg\n' % workingPath
	#Where is your OPUS installation?
	input = '%s%s/\n' % (input,opusPath)
	#Choose an address for provenance data collection.
	input = '%s\n' % input
	#Choose a location for the OPUS database to reside in
	input = '%s%s/output.db-%s-%d\n' % (input,workingPath,suffix,i)
	#Choose a location for the OPUS bash variables cfg_file
	input= '%s%s/.opus-vars\n' % (input,workingPath)
	#What is the location of your python 2.7 binary?
	input = '%s\n' % input
	#Where is your jvm installation?
	input = '%s/usr/lib/jvm/java-8-oracle\n' % input
	#Address to use for provenance server communications.
	input = '%s\n' % input
	#Set OPUS to debug mode
	input = '%sFalse\n' % input

	pipe.communicate(input=input.encode())
	
	baseCommand = '%s/bin/opusctl --conf %s/.opus-cfg %s' % (opusPath,workingPath,'%s')
	#Start Opus Server
	subprocess.call((baseCommand % 'server start').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Capture Provenance
	subprocess.call((baseCommand % ('process launch %s/test' % stagePath)).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	
	#Stop Opus Server
	subprocess.call((baseCommand % 'server stop').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Wait for Data Flushing
	time.sleep(2)
