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
sizes = [0 for i in range(0,len(graphs))]
for i in range(0,len(graphs)):
	# get graphs[i] and compute its size.
	# Somewhat redundant but avoids repeatedly computing sizes later
	# (and sometimes getting 0 for some reason)
	file = open(graphs[i], 'r')
	graph1 = fixIdentifier(file.read(), 1)
	file.close()
	g1nodes, g1edges, g1props = clingo2Dict(graph1)
	sizes[i] = len(g1nodes) + len(g1edges) + len(g1props)
	for j in range(0,i):
		map = processGraphBasic(readGraph(graphs[i], 1), readGRaph(graphs[j], 2), clingoCode, os.path.abspath('../'))
		if map != None:
			firstIso[i] = firstIso[j]

print(sizes)
print(firstIso)

numIsos = [0 for x in firstIso]

for i in firstIso:
	numIsos[i] = numIsos[i]+1

print(numIsos)
# find the largest equivalence class
maxIsos = max(numIsos)

if maxIsos <= 1:
	print("No pairs of isomorphic graphs found, deleting all and aborting")
	for n in graphs:
		os.remove(graphs[n])
	quit()


# delete all graphs not in the largest equivalence class
#for n in range(0,len(firstIso)):
#	if firstIso[n] != argmaxIsos:
#		os.remove(graphs[n])
#		print("deleted %s" % (graphs[n]))

# an equivalence class is trivial if it has only one element
# the "best" equivalence class is the one whose graphs are smallest among nontrivial ones

bestIso = None
minSize = None
for i in range(0,len(firstIso)):
	# if nontrivial
	if firstIso[i] == i and numIsos[i] > 1:
		# if better than best seen so far
		if minSize == None or sizes[i] < minSize:
			minSize = sizes[i]
			bestIso = i

print(bestIso)
print(minSize)
# make a list of all of the graphs in the best isomorphism class
bestGraphs = [graphs[i] for i in range(0,len(graphs))
			if firstIso[i] == bestIso]
print(bestGraphs)
# preserve some of them
preservedGraphs = [bestGraphs[0],bestGraphs[1]]
print(preservedGraphs)
# delete everything but the preserved class
for g in graphs:
	if g not in preservedGraphs:
		os.remove(g)
		print("deleted %s" % (g)) 
