#!/usr/bin/env python3

import os
import re
import sys
import time
import shutil
import subprocess
import json
import hashlib

#Merger Json
def mergeJson(base, line):
	lineObj = json.loads(line.rstrip())

	for typeKey in lineObj:
		#Loop through each new type section
		lineTypeObj = lineObj[typeKey]
		if typeKey in base.keys():
			#Type exists, add elements
			for itemKey in lineTypeObj:
				#Loop through each elements in type
				obj = lineTypeObj[itemKey]
				if itemKey in base[typeKey].keys():
					#Elements exists, merging data
					if isinstance(obj,str):
						#Simple Object (New String cover old String)
						base[typeKey][itemKey] = obj
					else:
						#Complex Object (Loop and add each properties)
						for objKey in obj:
							base[typeKey][itemKey][objKey] = obj[objKey]
				else:
					#Elements not exists, add full element
						base[typeKey][itemKey] = obj
		else:
		#Type not exists, add full type
			base[typeKey] = lineTypeObj
	return base

#Merge missing nodes from model
def mergeNode(base, model):
	elementKey = {'entity','agent','activity'}

	for typeKey in model:
		if typeKey in elementKey:
			#Type object
			typeObj = model[typeKey]
			if typeKey not in base:
				#Type not exist in base
				base[typeKey] = typeObj
			else:
				#Type exists in base
				baseObj = base[typeKey]
				for key in typeObj:
					if key not in baseObj:
						#New Node
						baseObj[key] = typeObj[key]
				#Replace base type json
				base[typeKey] = baseObj
	return base

#Start Camflow
def startCamflow(stagePath, workingPath, suffix, isModel):
	global camflowPath

	os.chdir(stagePath)

	#Fix config
	try:
		shutil.copyfile('/etc/camflowd.ini','/etc/camflowd.ini.backup')
		file = open('/etc/camflowd.ini','w')
		file.write('[general]\noutput=log\nformat=w3c\n[log]\npath=%s/audit.log' % workingPath)
		file.close()
	except IOError:
		pass

	#Clean camflow working history
#	subprocess.call('service camflowd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#	if os.path.exists('/tmp/.camflowModel'):
#		try:
#			mtime = os.path.getmtime('/tmp/.camflowModel')
#			with open('/proc/uptime', 'r') as f:
#				sec = float (f.readline().split()[0])
#			if (mtime < (time.time() - sec)):
#				os.remove('/tmp/.camflowModel' % workingPath)
#		except OSError:
#			pass

	#Capture provenance
	subprocess.call('service camflowd start'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	subprocess.call('camflow --opaque-file /usr/bin/bash false'.split())
	subprocess.call(('camflow --track-file %s/test propagate' % stagePath).split())
	subprocess.call('camflow --duplicate true'.split())
	subprocess.call('camflow -e true'.split())
#	subprocess.call('camflow -a true'.split())
	subprocess.call(('trace-cmd record -e syscalls %s/test' % stagePath).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#	subprocess.call('camflow -a false'.split())
	subprocess.call('camflow -e false'.split())
#	subprocess.call('camflow --duplicate false'.split())
	subprocess.call(('camflow --track-file %s/test false' % stagePath).split())
	time.sleep(1)
	subprocess.call('service camflowd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Handle FTrace Fingerprint
	ftraceResult = subprocess.check_output('trace-cmd report'.split())
	if ftraceResult:
		syscallList = [line.split(':')[1].strip() for line in ftraceResult.decode('ascii').split('\n') if re.match(r'^\s*test-((?!wait4).)*$',line)]
	
	fingerprint = hashlib.md5(''.join(syscallList).encode()).hexdigest()

	#Process provenance result into 1 json
	result={}
	try:
		file = open('%s/audit.log' % workingPath, 'r')
		next(file)
		for line in file:
			result = mergeJson(result, line.rstrip())
		file.close()
		os.remove('%s/audit.log' % workingPath)
	except Exception:
		pass

	#Write node to model (camflow will not republish node)
#	if os.path.exists('/tmp/.camflowModel'):
#		file = open('/tmp/.camflowModel', 'r')
#		line = file.read().rstrip()
#		oldNode = json.loads(line)
#		file.close()
#	else:
#		oldNode = dict()
#	file = open('/tmp/.camflowModel', 'w')
#	file.write(json.dumps(mergeNode(oldNode,result)))
#	file.close()

	#Handle fingerprint folder
	if not os.path.exists('%s/%s' %(workingPath, fingerprint)):
		os.makedirs('%s/%s' %(workingPath, fingerprint))
		os.chown('%s/%s' %(workingPath, fingerprint), 1000, 1000)

	if not isModel:
		#Writing result to json
		file = open('%s/%s/output.provjson-%s' %(workingPath, fingerprint, suffix), 'w')
		file.write(json.dumps(result))
		file.close()

	try:
		shutil.copyfile('/etc/camflowd.ini.backup','/etc/camflowd.ini')
	except IOError:
		pass

	return fingerprint

#Retrieve arguments
trial = 0
if len(sys.argv) == 8:
	if sys.argv[7].isdigit():
		trial = int(sys.argv[7])
elif len(sys.argv) != 7:
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Directory> <GCC MACRO> <CamFlow Config Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progPath = os.path.abspath(sys.argv[3])
macroOpt = sys.argv[4]
camflowPath = os.path.abspath(sys.argv[5])
suffix = sys.argv[6]

#Process GCC Macro
gccMacro = ""
for item in macroOpt.split(','):
        gccMacro = "%s -D%s" %(gccMacro,item)

fingerprintSet = set()

#Create Model Data
#subprocess.check_output(('%s/prepare %s %s --static' %(progPath, stagePath, gccMacro)).split())
#startCamflow(stagePath, workingPath, '', True)

for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s %s --static' %(progPath, stagePath, gccMacro)).split())
	fingerprintSet.add(startCamflow(stagePath, workingPath, '%s-%d' % (suffix, i), False))
	
for fingerprint in fingerprintSet:
	print (fingerprint)
