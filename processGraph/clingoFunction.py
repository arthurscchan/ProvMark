import re
import subprocess

#Fix Graph Identifier
def fixIdentifier(graph, graphNo):
	if not graph:
		return None

	identifier = graph[1:graph.index('(')]

	graph = graph.replace('n%s' % identifier, 'n%d' % graphNo)
	graph = graph.replace('e%s' % identifier, 'e%d' % graphNo)
	graph = graph.replace('l%s' % identifier, 'l%d' % graphNo)

	return graph

#Transform Clingo graph to Dict
def clingo2Dict(graph):
	nodeDict = set()
	edgeDict = set()
	propDict = dict()
	if not graph:
		return nodeDict, edgeDict, propDict
	for line in graph.split('\n'):
		if line.startswith("l"):
			#Properties
			#l1(<identifier>,<key>,<value>).
			match = re.match(r'.*\((.*),"(.*)","(.*)"\).*', line)
			if match.group(1) in propDict:
				prop = propDict[match.group(1)] 
			else:
				prop = dict()
			prop[match.group(2)] = match.group(3)
			propDict[match.group(1)] = prop
		elif line.startswith("e"):
			#Edges
			#e1(<identifier>,<node1>,<node2>,<type>).
			match = re.match(r'.*(\(.*\).*)', line)
			edgeDict.add(match.group(1))
		elif line.startswith("n"):
			#Nodes
			#n1(<identifier>,<type>).
			match = re.match(r'.*(\(.*\).*)', line)
			nodeDict.add(match.group(1))


	return nodeDict, edgeDict, propDict

#Transform final dictionary back to Clingo graph
def dict2Clingo(nodeDict, edgeDict, graphDict, suffix):
	result = ""
	
	for item in nodeDict:
		result = result + "n%s%s\n" %(suffix,item)
	for item in edgeDict:
		result = result + "e%s%s\n" %(suffix,item)
	for key in graphDict:
		props = graphDict[key]
		for propKey in props:
			result = result + "l%s(%s,\"%s\",\"%s\").\n" %(suffix, key, propKey, props[propKey])
	return result

#Retrieve mapping result from Clingo
def decodeClingoResult(result):
	map = dict()
	found = False
	for line in result.split('\n'):
		if line.startswith('match'):
			found = True
			for item in line.split():
				#match(<Graph1 identifier>, <Graph2 identifier>)
				match = re.match(r'match\((.*),(.*)\)', item)
				map[match.group(1)] = match.group(2)
		elif found:
			break
	return map

#Generalize properties of edges / vertics
def compareProps(graph1Props, graph2Props, isGeneral):
	result = dict()

	for key in set().union(graph1Props,graph2Props):
		if isGeneral:
		#Generalization of graph
			if key not in graph1Props or key not in graph2Props:
				#Key exists in one graph only
				result[key] = '?'
			elif graph1Props[key] == graph2Props[key]:
				#Key value pair keep the same in both graph
				result[key] = graph2Props[key]
			else:
				#Key value pair different in the two graph
				result[key] = '?'
		else:
		#Discover additional patterns
			if key not in graph1Props:
				#Key exists in syscall graph only (additional property)
				result[key] = graph2Props[key]
			elif key not in graph2Props:
				#Key exists in control graph only 
				#Should not reach here if we assume
				#Syscall graph always contains all info
				#from control graph. Reaching here may
				#indicate possible problems in graph matching
				#These dummy code is added to handle possible 
				#error rate in graph matching process resulting
				#in additional field in control graph
				continue;
			elif graph1Props[key] != graph2Props[key]:
				#Key value pair different in the two graph
				result[key] = graph2Props[key]
	return result

#Graph Process
def processGraph(graph1Path, graph2Path, clingoCode):
	#Read Graph
	file = open(graph1Path, 'r')
	graph1 = fixIdentifier(file.read(), 1)
	file.close()

	file = open(graph2Path,'r')
	graph2 = fixIdentifier(file.read(), 2)
	file.close()

	#Process Graph
	graph1Node, graph1Edge, graph1Props = clingo2Dict(graph1)
	graph2Node, graph2Edge, graph2Props = clingo2Dict(graph2)

	#Clingo Operation
	inputString = '%s\n%s\n%s'%(clingoCode, graph1, graph2)
	pipe = subprocess.Popen(['../clingo/clingo'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	mapResult = pipe.communicate(input=inputString.encode())[0]
	map = decodeClingoResult(mapResult.decode())

	return graph2Node, graph2Edge, graph1Props, graph2Props, map
