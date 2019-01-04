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
	nodeDict = dict()
	edgeDict = dict()
	propDict = dict()
	if not graph:
		return nodeDict, edgeDict, propDict
	for line in graph.split('\n'):
		if line.startswith("l"):
			#Properties
			#l1(<identifier>,<key>,<value>).
			match = re.match(r'l[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"(.*)\"[ ]*,[ ]*\"(.*)\"[ ]*\).', line)
			if match.group(1) in propDict:
				prop = propDict[match.group(1)] 
			else:
				prop = dict()
			prop[match.group(2)] = match.group(3)
			propDict[match.group(1)] = prop
		elif line.startswith("e"):
			#Edges
			#e1(<identifier>,<node1>,<node2>,<type>).
			match = re.match(r'e[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*([a-zA-Z0-9]*)[ ]*,[ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"([a-zA-Z0-9]*)\"[ ]*\).', line)
			edgeDict[match.group(1)] = (match.group(2),match.group(3),match.group(4))
		elif line.startswith("n"):
			#Nodes
			#n1(<identifier>,<type>).
			match = re.match(r'n[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"([a-zA-Z0-9]*)\"[ ]*\).', line)
			nodeDict[match.group(1)] = match.group(2)


	return nodeDict, edgeDict, propDict

#Transform final dictionary back to Clingo graph
def dict2Clingo(nodeDict, edgeDict, graphDict, suffix):
	result = ""
	
	for item in nodeDict:
		result = result + "n%s(%s,\"%s\").\n" %(suffix,item,nodeDict[item])
	for item in edgeDict:
		result = result + "e%s(%s,%s,%s,\"%s\").\n" %(suffix,item,edgeDict[item][0],edgeDict[item][1],edgeDict[item][2])
	for key in graphDict:
		props = graphDict[key]
		for propKey in props:
			result = result + "l%s(%s,\"%s\",\"%s\").\n" %(suffix, key, propKey, props[propKey])
	return result

#Retrieve mapping result from Clingo
def decodeClingoResult(result):
	for line in result.split('\n'):
		if line.startswith('UNSATISFIABLE'):
			return None
	map = dict()
	# get the last line starting with "match"
	lastline = None

	for line in result.split('\n'):
		if line.startswith('match'):
			lastline = line

	if lastline:
		for item in lastline.split():
			#match(<Graph1 identifier>, <Graph2 identifier>)
			match = re.match(r'match\((.*),(.*)\)', item)
			map[match.group(1)] = match.group(2)
	return map

#Retrieve edit distance from Clingo
def decodeEditDistance(result):
	found = False
	for line in result.split('\n'):
		if line.startswith('OPTIMUM FOUND'):
			found = True
		if (found and line.startswith('Optimization')):
		 	return  line[15:]
	return -1


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

#Call External Clingo
def clingoOperation(clingoCode, graph1, graph2, baseDir):
	inputString = '%s\n%s\n%s'%(clingoCode, graph1, graph2)
	pipe = subprocess.Popen(['%s/clingo/clingo' % baseDir, '--time-limit=600'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
	result = pipe.communicate(input=inputString.encode())[0]

	return result.decode()

def processGraphBasic(graph1Path, graph2Path, clingoCode, baseDir):
	file = open(graph1Path, 'r')
	graph1 = fixIdentifier(file.read(), 1)
	file.close()

	file = open(graph2Path,'r')
	graph2 = fixIdentifier(file.read(), 2)
	file.close()

	mapResult = clingoOperation(clingoCode, graph1, graph2, baseDir)

	graph1Node, graph1Edge, graph1Props = clingo2Dict(graph1)
	graph2Node, graph2Edge, graph2Props = clingo2Dict(graph2)
	
	map = decodeClingoResult(mapResult)
	return (graph1Node, graph1Edge, graph1Props), (graph2Node, graph2Edge, graph2Props), map

#Graph Process
def processGraph(graph1Path, graph2Path, clingoCode, baseDir, isMapping):
	#Read Graph
	file = open(graph1Path, 'r')
	graph1 = fixIdentifier(file.read(), 1)
	file.close()

	file = open(graph2Path,'r')
	graph2 = fixIdentifier(file.read(), 2)
	file.close()

	mapResult = clingoOperation(clingoCode, graph1, graph2, baseDir)
	
	if isMapping:
		#Process Graph
		graph1Node, graph1Edge, graph1Props = clingo2Dict(graph1)
		graph2Node, graph2Edge, graph2Props = clingo2Dict(graph2)
		
		map = decodeClingoResult(mapResult)		
		if map:
			return graph2Node, graph2Edge, graph1Props, graph2Props, map
		
		#Fail first time, remove properties
		graph1NodeEdge = ""
		for tmp in graph1.split('\n'):
			if tmp and not tmp.startswith('l'):
				graph1NodeEdge += "%s\n" % tmp
				
		graph2NodeEdge = ""
		for tmp in graph2.split('\n'):
			if tmp and not tmp.startswith('l'):
				graph2NodeEdge += "%s\n" % tmp
				
		mapResult = clingoOperation(clingoCode, graph1NodeEdge, graph2NodeEdge, baseDir)		
		map = decodeClingoResult(mapResult)		
		if map:
			return graph2Node, graph2Edge, graph1Props, graph2Props, map
		
		#Fail second time, return default mapping		
		for key in sorted(graph1Node.keys()):
			if key in graph2Node:
				map[key] = key
		for key in sorted(graph1Edge.keys()):
			if key in graph2Edge:
				map[key] = key
		return graph2Node, graph2Edge, graph1Props, graph2Props, map

	else:
		editDistance = decodeEditDistance(mapResult)
		return editDistance
