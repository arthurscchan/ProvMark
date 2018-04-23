#!/usr/bin/env python3

import os
import sys
import json

#Recover missing node
def addNode(identifier,counter):
	global suffix, id

	nodeType = ["activity","entity","agent"]

	file = open("/tmp/.camflowModel", "r")
	jsonString = next(file)
	file.close()
	obj = json.loads(jsonString)

	targetNode = None
	targetType = None
	
	for type in nodeType:
		if type in obj:
			if identifier in obj[type]:
				targetNode = obj[type][identifier]
				targetType = type
	
	if targetNode:
		dict[identifier] = counter
		id += "n%s(n%d,\"%s\").\n" % (suffix, counter, type)
		for labelIdentifier in targetNode:
			label += "l%s(n%d,\"%s\",\"%s\").\n" % (suffix, counter, labelIdentifier, targetNode[labelIdentifier])
		return True
	else:
		return False

#Generate Clingo graph string for nodes
def handleNode(type):
	global jsonObject, dict, id, label, counter, suffix
	
	if type in jsonObject:
		for nodeIdentifier in jsonObject[type]:
			node = jsonObject[type][nodeIdentifier]
			dict[nodeIdentifier] = counter
			id += "n%s(n%d,\"%s\").\n" % (suffix, counter, type)
#			label += "l%s(n%d,\"identifier\",\"%s\").\n" % (suffix, counter, nodeIdentifier)
			for labelIdentifier in node:
				label += "l%s(n%d,\"%s\",\"%s\").\n" % (suffix, counter, labelIdentifier, node[labelIdentifier])
			counter = counter+1

#Generate Clingo graph string for edges
def handleEdge(type, start, end):
	global jsonObject, dict, id, label, counter, suffix, nodeCounter

	if type in jsonObject:
		for edgeIdentifier in jsonObject[type]:
			edge = jsonObject[type][edgeIdentifier]

			#Recover missing node from model
			if edge[start] not in dict:
				if (addNode(edge[start],nodeCounter)):
					nodeCounter = nodeCounter + 1

			if edge[end] not in dict:
				if (addNode(edge[end],nodeCounter)):
					nodeCounter = nodeCounter + 1

			if edge[start] in dict and edge[end] in dict:
				id += "e%s(e%d,n%d,n%d,\"%s\").\n" %(suffix, counter, dict[edge[start]], dict[edge[end]], type)
#				label += "l%s(e%d,\"identifier\",\"%s\").\n" % (suffix, counter, edgeIdentifier)
				for labelIdentifier in edge:
					if labelIdentifier != start and labelIdentifier != end:
						label += "l%s(e%d,\"%s\",\"%s\").\n" % (suffix, counter, labelIdentifier, edge[labelIdentifier])
			counter = counter +1

#Check for correct numbers of arguments
if len(sys.argv) != 4:
	print ("Usage: %s <suffix> <Json Result from CamFlow> <Working Directory>" % sys.argv[0])
	quit()

jsonFile = sys.argv[2]

#Switch to working directory
os.chdir(os.path.abspath(sys.argv[3]))

#Process provenance result into 1 json
file = open(jsonFile, "r")
jsonString = next(file)
file.close()

#Intrepret Json
jsonObject = json.loads(jsonString)

id = ""
label = ""
counter = 1
dict = {}
suffix = sys.argv[1]

#Handle Nodes (activity, entity, agent)
handleNode("activity")
handleNode("entity")
handleNode("agent")

#Handle Edges (used, wasGeneratedBy, wasInformedBy, wasDerivedFrom)
nodeCounter = counter
counter = 1
handleEdge("used", "prov:activity", "prov:entity")
handleEdge("wasGeneratedBy", "prov:entity", "prov:activity")
handleEdge("wasInformedBy", "prov:informed", "prov:informant")
handleEdge("wasDerivedFrom", "prov:generatedEntity", "prov:usedEntity")

#Write result to output file
file = open("./clingo-%s" % suffix, "w")
file.write(id)
file.write(label)
file.close()

