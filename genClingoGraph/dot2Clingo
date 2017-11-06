#!/usr/bin/env python3

import os
import re
import sys

#Generate Clingo graph string for nodes
def handleNode(identifier, properties, counter):
	global dict, id, label, suffix
	
	dict[identifier] = counter
#	label += "l%s(n%d,\"identifier\",\"%s\").\n" % (suffix, counter, identifier)

	for props in properties.split("\\n"):
		(key,value) = props.split(':')
		if key == "type":
			id += "n%s(n%d,\"%s\").\n" % (suffix, counter, value)
		else:
			label += "l%s(n%d,\"%s\",\"%s\").\n" % (suffix, counter, key, value)

#Generate Clingo graph string for edges
def handleEdge(start, end, properties, counter):
	global dict, id, label, suffix

	if start in dict and end in dict:
		for props in properties.split("\\n"):
			(key,value) = props.split(':')
			if key == "type":
				id += "e%s(e%d, n%d, n%d, \"%s\").\n" %(suffix, counter, dict[start], dict[end], value)
			else:			
				label += "l%s(e%d,\"%s\",\"%s\").\n" % (suffix, counter, key, value)

#Check for correct numbers of arguments
if len(sys.argv) != 4:
	print ("Usage: %s <suffix> <Graphviz Dot Graph> <Working Directory>" % sys.argv[0])
	quit()

dotFile = sys.argv[2]

#Switch to working directory
os.chdir(os.path.abspath(sys.argv[3]))

#Separate node and edge record for handling
# Edge "<identifier1>" -> "<identifier2>" [label="<properties>" color="<color>" style="<style>"];
# Node "<identifier>" [label="<properties>" shape="<shape>" fillcolor="<fillcolor>"];
id = ""
label = ""
edgeCounter = 1
nodeCounter = 1
dict = {}
suffix = sys.argv[1]

file = open(dotFile, "r")
for line in file:
	nodeMatch = re.match(r'"(.*)" \[label="(.*)" shape="(.*)" fillcolor="(.*)"\];', line)
	edgeMatch = re.match(r'"(.*)" -> "(.*)" \[label="\((.*)\)" color="(.*)" style="(.*)"\];', line)	

	if nodeMatch:
		#Handle Node
		handleNode(nodeMatch.group(1), nodeMatch.group(2), nodeCounter)
		nodeCounter = nodeCounter + 1
	elif edgeMatch:
		#Handle Edge
		handleEdge(edgeMatch.group(1), edgeMatch.group(2), edgeMatch.group(3), edgeCounter)
		edgeCounter = edgeCounter + 1

file.close()

#Write result to output file
file = open("./clingo-%s" % suffix, "w")
file.write(id)
file.write(label)
file.close()

