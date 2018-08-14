#!/usr/bin/env python3

import os
import re
import sys
import subprocess
from clingoFunction import *

#Check for number graph
if len(sys.argv) < 6:
	print ("Usage: %s <Working Directory> <Clingo Code Template File> <suffix> <Graph1> <Graph2> [<Graph3> ...]" % sys.argv[0])
	quit()

workingDir = os.path.abspath(sys.argv[1])
suffix = sys.argv[3]

file = open(os.path.abspath(sys.argv[2]),'r')
clingoCode = file.read()
file.close()

result = dict()

os.chdir(workingDir)

for i in range(4,len(sys.argv)-1):
	graph2Node, graph2Edge, graph1Props, graph2Props, map = processGraph(sys.argv[i], sys.argv[i+1], clingoCode, True)

	#Generalize properties
	if map:
		tempDict = {}
		for graph1ID in map:
			if graph1ID in result:
				generalizedProps = compareProps(result[graph1ID], graph2Props[map[graph1ID]], True)
			else:
				generalizedProps = compareProps(graph1Props[graph1ID], graph2Props[map[graph1ID]], True)
			tempDict[map[graph1ID]] = generalizedProps
		result = tempDict
	else:
		result = graph2Props

#Transfer result to Clingo graph format
resultString = dict2Clingo(graph2Node, graph2Edge, result, suffix)

#Write result to output file
file = open("%s/general.clingo-%s" % (workingDir,suffix), "w")
file.write(resultString)
file.close()
