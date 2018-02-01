#!/usr/bin/env python3

import re
import os
import sys
import subprocess

#Remove hashcode from dump
def removeHashCode(dump):
	while True:
		index = dump.find('`hashCode`')
		if index == -1:
			break;
		endIndex = dump.find('", `', index)
		dump = dump[:index] + dump[endIndex+3:]
	return dump;

#Dump neo4j to cyhper query
def dumpFromDb(path):
	global baseDir,workingDir

	command = ['sudo', 'neo4j-shell', '-c', r'MATCH (n) MATCH ()-[r]-() REMOVE n.hashCode,r.hashCode;', '-config', ('%s/../config/neo4j.conf' % baseDir), '-path', '%s/%s' % (workingDir,path)]
	subprocess.call(command)

	command = "sudo neo4j-shell -c dump -config %s/../config/neo4j.conf -path %s/%s" % (baseDir,workingDir,path)
	dump = subprocess.check_output(command.split())
	return removeHashCode(dump.decode())

#Read cypher dump from file
def dumpFromFile(path):
	file = open(path, "r")
	dump = file.read()
	file.close()
	return removeHashCode(dump)

#Transform propString to propDictionary
def handleProperties(propString):
	propString = propString.replace('`','"')
	propString = propString.replace(':true',':1')
	propString = propString.replace(':false',':0')
	propDict = eval(propString)
	return propDict

#Generate Clingo graph string for nodes
def handleNode(identifier, properties, counter):
	global dict, id, label, suffix

	dict[identifier] = counter
#	label += "l%s(n%d,\"identifier\",\"%s\").\n" % (suffix, counter, identifier)

	propDict = handleProperties(properties)
	for key in propDict:
		if key == "type":
			id += "n%s(n%d,\"%s\").\n" % (suffix, counter, propDict[key])
		else:
			label += "l%s(n%d,\"%s\",\"%s\").\n" % (suffix, counter, key, propDict[key])

#Generate Clingo graph string for edges
def handleEdge(start, end, properties, counter):
	global dict, id, label, suffix

	if start in dict and end in dict:
		propDict = handleProperties(properties)
		if 'type' in propDict:
			id += "e%s(e%d,n%d,n%d,\"%s\").\n" %(suffix, counter, dict[start], dict[end], propDict['type'])
		else:
			id += "e%s(e%d,n%d,n%d,\"%s\").\n" %(suffix, counter, dict[start], dict[end], 'relatedTo')
		for key in propDict:
			if key != "type":
				label += "l%s(e%d,\"%s\",\"%s\").\n" % (suffix, counter, key, propDict[key])

#Check for correct numbers of arguments
if len(sys.argv) != 5 or (sys.argv[1] != "-d" and sys.argv[1] != "-c"):
	print ("Usage: %s -d <suffix> <Neo4j DB Path> <Working Directory>" % sys.argv[0])
	print ("Usage: %s -c <suffix> <Neo4j DB Cypher Dump File> <Working Directory>" % sys.argv[0])
	quit()

baseDir = os.path.abspath(os.path.dirname(sys.argv[0]))
workingDir = os.path.abspath(sys.argv[4])

if sys.argv[1] == "-d":
	cypherDump = dumpFromDb(sys.argv[3])
else:
	cypherDump = dumpFromFile(sys.argv[3])

#Separate node and edge record for handling
# Node 
#	create (<Identifier>:`VERTEX` {<Properties>})
#	create (<Identifier> {<Properties>})
# Edge 
#	create (<Identifier1>)-[:`.*` {<Properties>}]->(<Identifier2>)
#	create <Identifier1>-[:`.*` {<Properties>}]-><Identifier2>

id = ""
label = ""
nodeCounter = 1
edgeCounter = 1
dict = {}
suffix = sys.argv[2]

#Switch to working directory
os.chdir(workingDir)

for line in cypherDump.split('\n'):
	nodeMatch = re.match(r'create \((.*) ({.*})\)', line)
	edgeMatch = re.match(r'create \(?([^)]*)\)?-\[:`.*` ({.*})\]->\(?([^)]*)\)?', line)

	if nodeMatch:
		#Handle Node
		handleNode(nodeMatch.group(1).split(':`VERTEX`')[0], nodeMatch.group(2), nodeCounter)
		nodeCounter = nodeCounter + 1
	elif edgeMatch:
		#Handle Edge
		handleEdge(edgeMatch.group(1), edgeMatch.group(3), edgeMatch.group(2), edgeCounter)
		edgeCounter = edgeCounter + 1

#Write result to output file
file = open("./clingo-%s" % suffix, "w")
file.write(id)
file.write(label)
file.close()

