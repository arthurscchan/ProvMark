#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
from json_merger import Merger
from json_merger.config import UnifierOps, DictMergerOps

#Start Camflow
def startCamflow(stagePath, workingPath, suffix):
	global camflowPath

	os.chdir(stagePath)

	#Clean camflow working history
	subprocess.call('service camflowd stop'.split())
	subprocess.call(('rm -f %s/audit.log' % workingPath).split())

	#Initialize Config File
	shutil.copyfile('%s/camflowd.ini' % camflowPath, '%s/camflowd.ini.backup' % camflowPath)
	file = open('%s/camflowd.ini' % camflowPath, 'w')
	file.write('[general]\noutput=log\nlog=%s/audit.log\n' % workingPath)
	file.close()
	subprocess.call(('camflow --track-file %s/test propagate' % stagePath).split())

	#Capture provenance
	subprocess.check_call('service camflowd start'.split())

#	os.seteuid(1000)
	subprocess.Popen('%s/test' % stagePath).wait()
#	os.seteuid(0)

	subprocess.check_call('service camflowd stop'.split())

	#Process provenance result into 1 json
	file = open('%s/audit.log' % workingPath, 'r')
	next(file)
	result={}

	for line in file:
		print (line)
		m = Merger({},result,next(file).rstrip(),DictMergerOps.FALLBACK_KEEP_HEAD,UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST)
		m.merge()
		result = m.merged_root

	file.close()

	#Writing result to json
	file = open('%s/output.provjson-%s' %(workingPath, suffix), 'w')
	file.write(result)
	file.close()

	#Recover config file
	shutil.copyfile('%s/camflowd.ini.backup' % camflowPath, '%s/camflowd.ini' % camflowPath)
	os.remove('%s/camflowd.ini.backup' % camflowPath)

#Retrieve arguments
trial = 0
if len(sys.argv) == 7:
	if sys.argv[6].isdigit():
		trial = int(sys.argv[6])
elif len(sys.argv) != 6:
	print ("Usage: %s <Stage Directory> <Working Directory> <Program Directory> <CamFlow Config Directory> <suffix> [<Number of trial (Minimum / Default: 2)>" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[1])
workingPath = os.path.abspath(sys.argv[2])
progPath = os.path.abspath(sys.argv[3])
camflowPath = os.path.abspath(sys.argv[4])
suffix = sys.argv[5]

for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s' %(progPath, stagePath)).split())

	startCamflow(stagePath, workingPath, '%s-%d' % (suffix, i))
