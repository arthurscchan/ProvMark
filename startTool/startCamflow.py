#!/usr/bin/python3

import sys
import shutil
import subprocess
from json_merger import Merger
from json_merger.config import UnifierOps, DictMergerOps

#Check for correct numbers of arguments
if len(sys.argv) != 2:
	print ("Usage: %s <Benchmark Program>" % sys.argv[0])
	quit()

#Stop Camflow
subprocess.check_call("sudo service camflowd stop".split())

#Clean provenance file
subprocess.check_call("sudo rm -f /tmp/audit.log".split())

#Start Camflow
subprocess.check_call("sudo service camflowd start".split())

#Execute Benchmark File
subprocess.Popen(sys.argv[1]).wait()

#Stop Camflow
subprocess.check_call("sudo service camflowd stop".split())

#Copy log file to current location
shutil.copyfile("/tmp/audit.log","./result.log")

#Process provenance result into 1 json
file = open("./result.log", "r")
next(file)
result={}

for line in file:
	m = Merger({},result,next(file).rstrip(),DictMergerOps.FALLBACK_KEEP_HEAD,UnifierOps.KEEP_UPDATE_AND_HEAD_ENTITIES_HEAD_FIRST)
	m.merge()
	result = m.merged_root

file.close()

#Writing result to json
file = open("./result.json","w")
file.write(result)
file.close()
