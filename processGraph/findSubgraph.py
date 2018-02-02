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

# Properties are present if present in graph 2 and not in linked part of graph 1
diffProps = dict()
for graph2ID in graph2Props:
	if graph2ID not in map.values():
		tempDict = dict()
		props = graph2Props[graph2ID]
		for key in props:
			if (props[key] != '?'):
				tempDict[key] = props[key]
		if tempDict:
			diffProps[graph2ID] = tempDict
	else:
		for x in map:
			if (map[x] == graph2ID):
				graph1ID = x
		tempDict = dict()
		props1 = graph1Props[graph1ID]
		props2 = graph2Props[graph2ID]
		for key in props2:	
			if (props2[key] != '?' 
			    and (key not in props1 
			         or props1[key] != props2[key])):
				tempDict[key] = props2[key]
		if tempDict:
			diffProps[graph2ID] = tempDict

# Edges are present if present in graph2 and not linked to anything in map

incidentNodes = set()
diffEdge = dict()
for graph2ID in graph2Edge:
	if (graph2ID in diffProps
	    or graph2ID not in map.values()):
		diffEdge[graph2ID] = graph2Edge[graph2ID]
		incidentNodes = incidentNodes | set([graph2Edge[graph2ID][0],graph2Edge[graph2ID][1]])

#Nodes are present if there is an incident edge or property or if linked to anything in map
diffNode = dict()
for graph2ID in graph2Node:
	if ((graph2ID in incidentNodes) and (diffProps.keys() or graph2ID not in map.values())):
		diffNode[graph2ID] = graph2Node[graph2ID]



#Transfer result to Clingo graph format
resultString = dict2Clingo(diffNode, diffEdge, diffProps, suffix)

#Write result to output file
file = open(outFile, "w")
file.write(resultString)
file.close()
