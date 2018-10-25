#!/usr/bin/env python3

import os
import re
import sys
import time
import hashlib
import subprocess

#Retrieve arguments
if len(sys.argv) != 6:	
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Name> <OPUS Directory> <suffix>" % sys.argv[0])
	quit()

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progName = sys.argv[3]
opusPath = os.path.abspath(sys.argv[4])
suffix = sys.argv[5]

#Prepare OPUS wrapper
os.chdir(opusPath)
subprocess.call('./update-wrapper')

os.chdir(workingPath)

#Get Audit Log

	#Capture Provenance
subprocess.call((baseCommand % ('process launch %s/test' % stagePath)).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.call('trace-cmd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.call(('trace-cmd extract -o %s/trace.dat' % workingPath).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
=======
#Config OPUS Server
pipe = subprocess.Popen(['%s/bin/opusctl' % opusPath, 'conf'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)

#Choose a location for the OPUS master config
config = '%s/.opus-cfg\n' % workingPath
#Where is your OPUS installation?
config = '%s%s/\n' % (config,opusPath)
#Choose an address for provenance data collection.
config = '%s\n' % config
#Choose a location for the OPUS database to reside in
config = '%s%s/output.db\n' % (config,workingPath)
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

if os.path.exists('%s/trace.dat' % workingPath):
	os.remove('%s/trace.dat' % workingPath)

subprocess.call('trace-cmd reset'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.call('trace-cmd start -e syscalls'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#Capture Provenance
subprocess.call((baseCommand % ('process launch %s/%s' % (stagePath,progName))).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	
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

#Handle fingerprint folder
if not os.path.exists('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint)):
	os.makedirs('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint))
	os.chown('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint), 1000, 1000)

os.rename('%s/output.db' % workingPath,'%s/%s-%s/output.db-%s-%d' % (workingPath, suffix.split('-')[0], fingerprint, suffix, i))

print(fingerprint)
