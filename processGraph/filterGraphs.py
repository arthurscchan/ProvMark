#!/usr/bin/env python3

import os
import re
import sys
import subprocess
from clingoFunction import *

#Check for number graph
if len(sys.argv) < 4:
	print ("Usage: %s <Working Directory> <Clingo Code Template File> <Graph1> [<Graph2> <Graph3> ...]" % sys.argv[0])
	quit()

workingDir = os.path.abspath(sys.argv[1])

file = open(os.path.abspath(sys.argv[2]),'r')
clingoCode = file.read()
file.close()

result = dict()

os.chdir(workingDir)

graphs = []

for i in range(3,len(sys.argv)):
	graphs.append(sys.argv[i])


if len(graphs) == 1:
	print("Only one graph provided")
	quit()
# for each graph keep track of the first graph in graphs isomorphic to it (initially this is itself)

firstIso = [i for i in range(0,len(graphs))]
for i in range(0,len(graphs)):
	for j in range(0,i):
		g1, g2, map = processGraphBasic(readGraph(graphs[i], 1), readGraph(graphs[j], 2), clingoCode, os.path.abspath('../'))
		if map != None and firstIso[i] == i:
			firstIso[i] = j
		      
numIsos = [0 for x in firstIso]

for i in firstIso:
        numIsos[i] = numIsos[i]+1

# find the largest equivalence class
maxIsos = 0
argmaxIsos = -1
for n in range(0,len(numIsos)):
       if numIsos[n] > maxIsos:
               maxIsos = numIsos[n]
               argmaxIsos = n

if maxIsos == 1:
        print("No pairs of isomorphic graphs found, aborting")
        quit()

# delete all graphs not in the largest equivalence class
for n in range(0,len(firstIso)):
        if firstIso[n] != argmaxIsos:
                os.remove(graphs[n])
                print("deleted %s" % (graphs[n]))
