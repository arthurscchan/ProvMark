#!/usr/bin/env python3

import os
import sys
from clingoFunction import *

#Check for number graph
if len(sys.argv) != 7:
	print ("Usage: %s <Working Directory> <Clingo Code Template File> <suffix> <Control Graph> <Target Graph> <Output File>" % sys.argv[0])
	quit()

workingDir = os.path.abspath(sys.argv[1])
suffix = sys.argv[3]
outFile = os.path.abspath(sys.argv[6])
result = dict()

file = open(os.path.abspath(sys.argv[2]),'r')
clingoCode = file.read()
file.close()

os.chdir(workingDir)

#Process Graph
graph2Node, graph2Edge, graph1Props, graph2Props, map = processGraph(sys.argv[4], sys.argv[5], clingoCode)

#Handle vertics / edges exist in both graph
for graph1ID in map:
	#Existing branches
	generalizedProps = compareProps(graph1Props[graph1ID], graph2Props[map[graph1ID]], False)
	tempDict = dict()
	for key in generalizedProps:
		if generalizedProps[key] != '?':
			tempDict[key] = generalizedProps[key]
	if len(tempDict) > 0:
		result[map[graph1ID]] = tempDict

#Handle vertics / edge exist in syscall graph
for graph2ID in graph2Props:
	if graph2ID not in map.values():
		#Additional branches
		tempDict = dict()
		props = graph2Props[graph2ID]
		for key in props:
			if (props[key] != '?'):
				tempDict[key] = props[key]
		result[graph2ID] = tempDict

#Transfer result to Clingo graph format
resultString = dict2Clingo(graph2Node, graph2Edge, result, suffix)

#Write result to output file
file = open(outFile, "w")
file.write(resultString)
file.close()
