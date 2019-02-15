#!/usr/bin/env python3

import os
import re
import sys
import time
import shutil
import hashlib
import subprocess

#Start SPADE with config
def startSpade(workingPath, suffix, loopCount, fingerprint):
	global isNeo4j, spadePath

	#Handle fingerprint folder
	if not os.path.exists('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint)):
		os.makedirs('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint))
		os.chown('%s/%s-%s' %(workingPath, suffix.split('-')[0], fingerprint), 1000, 1000)

	#Initialize Config File
	try:
		shutil.copyfile('%s/cfg/spade.config' % spadePath, '%s/cfg/spade.config.backup' % spadePath)
	except:
		pass
	file = open('%s/cfg/spade.config' % spadePath, 'w')
	file.write('add reporter Audit inputLog=%s/%s-input.log arch=64 fileIO=true\n' % (workingPath,suffix))
	if isNeo4j:
		file.write('add storage Neo4j %s/%s-%s/output.db-%s\n' % (workingPath, suffix.split('-')[0], fingerprint, suffix))
	else:
		file.write('add storage Graphviz %s/%s-%s/output.dot-%s\n' % (workingPath, suffix.split('-')[0], fingerprint, suffix))
	file.close()

	#Start SPADE
	spadeStart = '%s/bin/spade start' % spadePath
	subprocess.call(spadeStart.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	time.sleep(loopCount)	

	#Stop SPADE
	spadeStop = '%s/bin/spade stop' % spadePath
	subprocess.call(spadeStop.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	time.sleep(loopCount)

	#Recover config file
	shutil.copyfile('%s/cfg/spade.config.backup' % spadePath, '%s/cfg/spade.config' % spadePath)
	os.remove('%s/cfg/spade.config.backup' % spadePath)

#Retrieve arguments
if len(sys.argv) != 7 or (sys.argv[1] != '-n' and sys.argv[1] != '-d'):
	print ("Neo4j DB Output Usage: %s -n <Stage Directory> <Working Directory> <Program Name> <SPADE Directory> <suffix>" % sys.argv[0])
	print ("Graphviz DOT Output Usage: %s -d <Stage Directory> <Working Directory> <Program Name> <SPADE Directory> <suffix>" % sys.argv[0])
	quit()

stagePath = os.path.abspath(sys.argv[2])
workingPath = os.path.abspath(sys.argv[3])
isNeo4j = (sys.argv[1] == '-n')
progName = sys.argv[4]
spadePath = os.path.abspath(sys.argv[5])
suffix = sys.argv[6]

#Add audit rule for capturing audit log of activities (according to spade default)
rule0 = 'auditctl -D'
rule1 = 'auditctl -a exit,always -F arch=b64 -F euid=1000 -S kill -S exit -S exit_group -S connect' 
rule2 = 'auditctl -a exit,always -F arch=b64 -F euid=1000 -S mmap -S mprotect -S unlink -S unlinkat -S link -S linkat -S symlink -S symlinkat -S clone -S fork -S vfork -S execve -S open -S close -S creat -S openat -S mknodat -S mknod -S dup -S dup2 -S dup3 -S fcntl -S bind -S accept -S accept4 -S socket -S rename -S renameat -S setuid -S setreuid -S setresuid -S setgid -S setregid -S setresgid -S chmod -S fchmod -S fchmodat -S pipe -S pipe2 -S truncate -S ftruncate -S read -S pread -S write -S pwrite -S creat -F success=1'
subprocess.check_output(rule0.split())
subprocess.check_output(rule1.split())
subprocess.check_output(rule2.split())

#Get Audit Log
os.chdir(stagePath)

if os.path.exists('%s/trace.dat' % workingPath):
	os.remove('%s/trace.dat' % workingPath)

subprocess.call('trace-cmd reset'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.call('trace-cmd start -e syscalls'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

time.sleep(5)

file = open('/var/log/audit/audit.log','a')
file.write('start-start\n')
file.close()

os.seteuid(1000)
subprocess.check_call('%s/%s' % (stagePath,progName))
os.seteuid(0)

time.sleep(1)

file = open('/var/log/audit/audit.log','a')
file.write('end-end\n')
file.close()

fingerprint = hashlib.md5(''.join(syscallList).encode()).hexdigest()

subprocess.check_output(rule0.split())

#Handle Aduit Log File
shutil.copyfile('/var/log/audit/audit.log', '%s/audit.log' % workingPath)

#Generate graph
#Extract audit log line for each trial
command = 'grep -n %s %s/audit.log' % ('%s', workingPath)

grepCommand = command % ('start-start')
tempResult = subprocess.check_output(grepCommand.split()).decode().splitlines()
totalLine = len(tempResult)
start = int(tempResult[totalLine-1].split(':')[0]) + 1

grepCommand = command % ('end-end')
tempResult = subprocess.check_output(grepCommand.split()).decode().splitlines()
totalLine = len(tempResult)
end = int(tempResult[totalLine-1].split(':')[0]) - 2

inFile = open('%s/audit.log' % workingPath, 'r')
inputLog = '%s/%s-%d-input.log' % (workingPath,suffix,i)
outFile = open(inputLog, 'w')
for c, line in enumerate(inFile):
	if (c >= start and c <= end):
		outFile.write(line)

inFile.close()
outFile.close()

if not isNeo4j:
	if os.path.getsize(inputLog) == 0:
		continue

	#Send log lines to SPADE for processing (Repeat if data is empty)
	outFile = '%s/%s-%s/output.dot-%s' % (workingPath, suffix.split('-')[0], fingerprint, suffix)
	loopCount = 0
	while not os.path.exists(outFile) or os.path.getsize(outFile) <= 162:
		loopCount = loopCount + 1
		startSpade(workingPath, '%s' % suffix, loopCount, fingerprint)
else:
	startSpade(workingPath, '%s' % suffix, 2, fingerprint)

print (fingerprint)
