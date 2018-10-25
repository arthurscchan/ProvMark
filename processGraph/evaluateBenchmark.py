#!/usr/bin/env python3

import os
import sys
from clingoFunction import *

#Check for argument
if len(sys.argv) != 2:
        print ("Usage: %s <Working Directory>" % sys.argv[0])
        quit()

workingDir = os.path.abspath(sys.argv[1])
benchmarkDir = os.path.abspath('%s/benchmark' % sys.argv[1])

os.chdir(workingDir)

# Process testing program provenance graph
with open("%s/clingo-testing" % workingDir, "r") as file:
	graphNode, graphEdge, graphProps = clingo2Dict(fixIdentifier(file.read(), 1))

# Process benchmark graph
benchmarkList = list()
for path in ['%s/%s' % (benchmarkDir,name) for name in os.listdir(benchmarkDir)]:
	with open(path, "r") as file:
		node, edge, props = clingo2Dict(fixIdentifier(file.read(), 1))
		benchmarkList.append({'node':node, 'edge':edge, 'props':props})

