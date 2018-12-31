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
	if not os.path.exists('%s/%s' %(workingPath, fingerprint)):
		os.makedirs('%s/%s' %(workingPath, fingerprint))
		os.chown('%s/%s' %(workingPath, fingerprint), 1000, 1000)

	#Initialize Config File
	try:
		shutil.copyfile('%s/cfg/spade.config' % spadePath, '%s/cfg/spade.config.backup' % spadePath)
	except:
		pass
	file = open('%s/cfg/spade.config' % spadePath, 'w')
	file.write('add reporter Audit inputLog=%s/input.log arch=64 fileIO=true\n' % workingPath)
	if isNeo4j:
		file.write('add storage Neo4j %s/%s/output.db-%s\n' % (workingPath, fingerprint, suffix))	
	else:
		file.write('add storage Graphviz %s/%s/output.dot-%s\n' % (workingPath, fingerprint, suffix))
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
trial = 0
if len(sys.argv) == 9:
	if sys.argv[8].isdigit():
		trial = int(sys.argv[8])
elif len(sys.argv) != 8 or (sys.argv[1] != '-n' and sys.argv[1] != '-d'):
	print ("Neo4j DB Output Usage: %s -n <Stage Directory> <Working Directory> <Program Directory> <GCC Marco> <SPADE Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	print ("Graphviz DOT Output Usage: %s -d <Stage Directory> <Working Directory> <Program Directory> <GCC Macro> <SPADE Directory> <suffix> [<Number of trial (Minimum / Default: 2)>]" % sys.argv[0])
	quit()

if trial < 2:
	trial = 2

stagePath = os.path.abspath(sys.argv[2])
workingPath = os.path.abspath(sys.argv[3])
isNeo4j = (sys.argv[1] == '-n')
progPath = os.path.abspath(sys.argv[4])
macroOpt = sys.argv[5]
spadePath = os.path.abspath(sys.argv[6])
suffix = sys.argv[7]

#Process GCC Macro
gccMacro = ""
for item in macroOpt.split(','):
	gccMacro = "%s -D%s" %(gccMacro,item)

#Add audit rule for capturing audit log of activities (according to spade default)
rule0 = 'auditctl -D'
rule1 = 'auditctl -a exit,always -F arch=b64 -F euid!=0 -S kill -S exit -S exit_group -S connect' 
rule2 = 'auditctl -a exit,always -F arch=b64 -F euid!=0 -S mmap -S mprotect -S unlink -S unlinkat -S link -S linkat -S symlink -S symlinkat -S clone -S fork -S vfork -S execve -S open -S close -S creat -S openat -S mknodat -S mknod -S dup -S dup2 -S dup3 -S fcntl -S bind -S accept -S accept4 -S socket -S rename -S renameat -S setuid -S setreuid -S setgid -S setregid -S chmod -S fchmod -S fchmodat -S pipe -S pipe2 -S truncate -S ftruncate -S read -S pread -S write -S pwrite -S creat -F success=1'
subprocess.check_output(rule0.split())
subprocess.check_output(rule1.split())
subprocess.check_output(rule2.split())

fingerprintList = []

#Get Audit Log
for i in range(1, trial+1):
	#Prepare the benchmark program
	subprocess.check_output(('%s/prepare %s %s --static' % (progPath,stagePath,gccMacro)).split())

	os.chdir(stagePath)

	#Ensure no one writing to the file
	while True:
		if time.time() > os.path.getmtime('/var/log/audit/audit.log') + 1:
			break;
	

	subprocess.call('trace-cmd start -e syscalls'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)	

	file = open('/var/log/audit/audit.log','a')
	file.write('start%dstart%d\n' % (i,i))
	file.close()

	os.seteuid(1000)
	os.system('%s/test' % stagePath)
	os.seteuid(0)

	#Ensure no one writing to the file
	while True:
		if time.time() > os.path.getmtime('/var/log/audit/audit.log') + 1:
			break;

	file = open('/var/log/audit/audit.log','a')
	file.write('end%dend%d\n' % (i,i))
	file.close()

	subprocess.call('trace-cmd stop'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)	
	subprocess.call(('trace-cmd extract -o %s/trace.dat' % (workingPath)).split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)	

	#Handle FTrace Fingerprint
	ftraceResult = subprocess.check_output(('trace-cmd report -i %s/trace.dat' % (workingPath)).split(), stderr=subprocess.DEVNULL)
	if ftraceResult:
		syscallList = [line.split(':')[1].strip() for line in ftraceResult.decode('ascii').split('\n') if re.match(r'^\s*test-((?!wait4).)*$',line)]
	fingerprintList.append(hashlib.md5(''.join(syscallList).encode()).hexdigest())

subprocess.check_output(rule0.split())

#Handle Aduit Log File
shutil.copyfile('/var/log/audit/audit.log', '%s/audit.log' % workingPath)

#Generate graph for multiple trial 
for i in range(1, trial+1):
#	print ('Trial %d start' % i)

	#Extract audit log line for each trial
	command = 'grep -n %s %s/audit.log' % ('%s', workingPath)

	grepCommand = command % ('start%dstart%d' % (i,i))
	tempResult = subprocess.check_output(grepCommand.split()).decode().splitlines()
	totalLine = len(tempResult)
	start = int(tempResult[totalLine-1].split(':')[0]) + 1

	grepCommand = command % ('end%dend%d' % (i,i))
	tempResult = subprocess.check_output(grepCommand.split()).decode().splitlines()
	totalLine = len(tempResult)
	end = int(tempResult[totalLine-1].split(':')[0]) - 1

	inFile = open('%s/audit.log' % workingPath, 'r')
	outFile = open('%s/input.log' % workingPath, 'w')
	for c, line in enumerate(inFile):
		if (c >= start and c < end):
			outFile.write(line)

	inFile.close()
	outFile.close()

	if not isNeo4j:
		#Send log lines to SPADE for processing (Repeat if data is empty)
		outFile = '%s/%s/output.dot-%s-%d' % (workingPath, fingerprintList[i-1], suffix, i)
		loopCount = 0
		while not os.path.exists(outFile) or os.path.getsize(outFile) < 1000:
			loopCount = loopCount + 1
			startSpade(workingPath, '%s-%d' %(suffix,i), loopCount, fingerprintList[i-1])
	else:
		startSpade(workingPath, '%s-%d' %(suffix,i), 2, fingerprintList[i-1])

#	print ('Trial %d end' % i)

for fingerprint in set(fingerprintList):
	print (fingerprint)
