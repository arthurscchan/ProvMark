#!/usr/bin/env python3

import os
import sys
from clingoFunction import *

#Check for argument
if len(sys.argv) != 2:
        print ("Usage: %s <Working Directory>" % sys.argv[0])
        quit()

baseDir = os.path.abspath('%s/../' % sys.argv[1])
workingDir = os.path.abspath(sys.argv[1])
benchmarkDir = os.path.abspath('%s/benchmark' % sys.argv[1])

os.chdir(workingDir)

# Process testing program provenance graph
graph = readGraph("%s/clingo-testing" % workingDir, 1)
graphNode, graphEdge, graphProps = clingo2Dict(graph)

# Process benchmark graph
benchmarkList = list()
for path in ['%s/%s' % (benchmarkDir,name) for name in os.listdir(benchmarkDir)]:
	benchmark = readGraph(path, 1)
	node, edge, props = clingo2Dict(benchmark)
	benchmarkList.append({'graph':benchmark, 'node':node, 'edge':edge, 'props':props})

#benchmarkEditDistance = list()
#for benchmark in benchmarkList:
#	benchmark
