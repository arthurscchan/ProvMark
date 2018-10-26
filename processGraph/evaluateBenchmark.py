#!/usr/bin/env python3

import os
import sys
from clingoFunction import *

#Check for argument
if len(sys.argv) != 4:
        print ("Usage: %s <Working Directory> <Clingo Code Template File> <threshold>" % sys.argv[0])
        quit()

baseDir = os.path.abspath('%s/../' % sys.argv[1])
workingDir = os.path.abspath(sys.argv[1])
benchmarkDir = os.path.abspath('%s/benchmark' % sys.argv[1])
if sys.argv[2].isdigit():
	threshold = int(sys.argv[2])
else:
	threshold = 0

file = open(os.path.abspath(sys.argv[2]),'r')
clingoCode = file.read()
file.close()

os.chdir(workingDir)

# Process testing program provenance graph
graph = readGraph("%s/clingo-testing" % workingDir, 1)
graphNode, graphEdge, graphProps = clingo2Dict(graph)

# Process benchmark graph
found = False
minEditDistance = sys.maxsize
for path in ['%s/%s' % (benchmarkDir,name) for name in os.listdir(benchmarkDir)]:
	benchmark = readGraph(path, 1)
	editDistance = processGraph(graph, benchmark, clingoCode, baseDir, False)
	if editDistance.isdigit():
		if minEditDistance > int(editDistance):
			minEditDistance = int(editDistance)
			benchmarkNode, benchmarkEdge, benchmarkProps = clingo2Dict(benchmark)
			found = True

if found:
	#Total number of elements of the testing program minus total number of elements of the benchmark
	difference = len(graphNode) + len(graphEdge) + len(graphProps) - len(benchmarkNode) - len(benchmarkEdge) - len(benchmarkProps)

	#If sum of threshold and the difference larger than or equal to edit distance, then pattern exists.
	if (difference + threshold) >= editDistance:
		print ('%d/%d/' % (editDistance, difference + threshold))
	else
		print ('%d/%d/ not' % (editDistance, difference + threshold))
else:
	print ('%d/%d not' % (len(graphNode) + len(graphEdge) + len(graphProps), difference + threshold))
