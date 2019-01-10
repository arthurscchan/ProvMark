#!/usr/bin/env python3

import os
import re
import sys
import time
import hashlib
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
macroOpt = sys.argv[4]
opusPath = os.path.abspath(sys.argv[5])
suffix = sys.argv[6]

#Process GCC Macro
gccMacro = ""
for item in macroOpt.split(','):
        gccMacro = "%s -D%s" %(gccMacro,item)

#Prepare OPUS wrapper
os.chdir(opusPath)
subprocess.call('./update-wrapper')

os.chdir(workingPath)

fingerprintSet = set()

#Get Audit Log
for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s %s' % (progPath, stagePath, gccMacro)).split())

	#Config OPUS Server
	pipe = subprocess.Popen(['%s/bin/opusctl' % opusPath, 'conf'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

	#Choose a location for the OPUS master config
	config = '%s/.opus-cfg\n' % workingPath
	#Where is your OPUS installation?
	config = '%s%s/\n' % (config, opusPath)
	#Choose an address for provenance data collection.
	config = '%s\n' % config
	#Choose a location for the OPUS database to reside in
	config = '%s%s/output.db\n' % (config, workingPath)
	#Choose a location for the OPUS bash variables cfg_file
	config = '%s%s/.opus-vars\n' % (config, workingPath)
	#What is the location of your python 2.7 binary?
	config = '%s\n' % config
	#Where is your jvm installation?
	config = '%s/usr/lib/jvm/java-8-oracle\n' % config
	#Address to use for provenance server communications.
	config = '%s\n' % config
	#Set OPUS to debug mode
	config = '%sFalse\n' % config

	pipe.communicate(input=config.encode())

	baseCommand = '%s/bin/opusctl --conf %s/.opus-cfg %s' % (opusPath, workingPath, '%s')
	#Start Opus Server
	subprocess.call((baseCommand % 'server start').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	if os.path.exists('%s/trace.dat' % workingPath):
		os.remove('%s/trace.dat' % workingPath)

	subprocess.call('trace-cmd reset'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.call('trace-cmd start -e syscalls'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Capture Provenance
	subprocess.call((baseCommand % ('process launch %s/test' % stagePath)).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	subprocess.call('trace-cmd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.call(('trace-cmd extract -o %s/trace.dat' % workingPath).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	
	#Stop Opus Server
	subprocess.call((baseCommand % 'server stop').split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Ensure Opus Server stopped
	while True:
		time.sleep(2)
		try:
			output = subprocess.check_output((baseCommand % 'server status').split(), stderr=subprocess.DEVNULL)
		except subprocess.CalledProcessError as err:
			#Unlucky situation as opus server is disconnected but the process is not yet completed
			#Treated as server stopped
			break
		if 'Server is not running.' in output.decode():
			break

	#Handle FTrace Fingerprint
	ftraceResult = subprocess.check_output(('trace-cmd report -i %s/trace.dat' % workingPath).split(), stderr=subprocess.DEVNULL)
	if ftraceResult:
		syscallList = [line.split(':')[1].strip() for line in ftraceResult.decode('ascii').split('\n') if re.match(r'^\s*test-((?!wait4).)*$',line)]

	fingerprint = hashlib.md5(''.join(syscallList).encode()).hexdigest()
	fingerprintSet.add(fingerprint)

	#Handle fingerprint folder
	if not os.path.exists('%s/%s-%s' %(workingPath, suffix, fingerprint)):
		os.makedirs('%s/%s-%s' %(workingPath, suffix, fingerprint))
		os.chown('%s/%s-%s' %(workingPath, suffix, fingerprint), 1000, 1000)

	os.rename('%s/output.db' % workingPath,'%s/%s-%s/output.db-%s-%d' % (workingPath, suffix, fingerprint, suffix, i))

for fingerprint in fingerprintSet:
	print(fingerprint)
