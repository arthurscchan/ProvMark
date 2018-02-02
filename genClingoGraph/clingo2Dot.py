#!/usr/bin/env python3

import re
import sys

#Check for correct numbers of arguments
if len(sys.argv) != 3:
	print ("Usage: %s <Clingo Graph> <Output Graph>" % sys.argv[0])
	quit()

clingoFile = sys.argv[1]

#Separate node and edge record for handling
# Clingo Edge "e1(e?,n?,n?,<type>)."
# Clingo Node "n1(n?,"<type>")."
# Clingo Label "l1(??,<name>,<value>)."

edge = {}
node = {}
label = {}

file = open(clingoFile, "r")
clingo = file.read()
file.close()

for line in clingo.split("\n"):
	nodeMatch = re.match(r'n[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"([a-zA-Z0-9]*)\"[ ]*\).', line)
	edgeMatch = re.match(r'e[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*([a-zA-Z0-9]*)[ ]*,[ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"([a-zA-Z0-9]*)\"[ ]*\).', line)
	labelMatch = re.match(r'l[a-zA-Z0-9]*\([ ]*([a-zA-Z0-9]*)[ ]*,[ ]*\"(.*)\"[ ]*,[ ]*\"(.*)\"[ ]*\).', line)

	if nodeMatch:
		#Add Node
		if nodeMatch.group(1) not in node:
			node[nodeMatch.group(1)] = nodeMatch.group(2)
	elif edgeMatch:
		#Add Edge
		if edgeMatch.group(2) not in node:
			node[edgeMatch.group(2)] = "Dummy"
		elif edgeMatch.group(3) not in node:
			node[edgeMatch.group(3)] = "Dummy"

		if edgeMatch.group(1) not in edge:
			tempDict = {}
			tempDict['from'] = edgeMatch.group(2)
			tempDict['to'] = edgeMatch.group(3)
			tempDict['type'] = edgeMatch.group(4)
			edge[edgeMatch.group(1)] = tempDict
	elif labelMatch:
		#Add Label
		labelText = ""
		if labelMatch.group(1) in label:
			labelText = label[labelMatch.group(1)]
		labelText = "%s\\n%s:%s" %(labelText,labelMatch.group(2),labelMatch.group(3))
		label[labelMatch.group(1)] = labelText

# Dot Node "<identifier>" [label="<properties>" shape="<shape>" fillcolor="<fillcolor>"];
# Dot Edge "<identifier1>" -> "<identifier2>" [label="<properties>" color="<color>" style="<style>"];
nodeTemplate = "\"%s\" [label=\"%s\" shape=\"%s\" fillcolor=\"%s\"];\n" 
edgeTemplate = "\"%s\" -> \"%s\" [label=\"%s\" color=\"blue\" style=\"solid\"];\n"

#Write result to output file
file = open(sys.argv[2], "w")
file.write("digraph clingo2dot {\n")
file.write("graph [rankdir = \"RL\"];\n")
file.write("node [fontname=\"Helvetica\" fontsize=\"8\" style=\"filled\" margin=\"0.0,0.0\"];\n")
file.write("edge [fontname=\"Helvetica\" fontsize=\"8\"];\n")
# Build Node Statement
for key in node:
	found = False
	for edgeKey in edge:
		item = edge[edgeKey]
		if item['from'] == key or item['to'] == key:
			found = True
			break;
	if not found:
		continue;
	#Default shape and color for process
	shape = 'box'
	fillcolor = "lightsteelblue1"

	if node[key] == "Dummy":
		nodeLabel = "Dummy Node"
		shape = "ellipse"
		fillcolor = "green"
	else:
		if key in label:
			nodeLabel = "%s\\ntype:%s" %(label[key],node[key])
		else:
			nodeLabel = "type:%s" % node[key]
		if node[key] == "Artifact" or node[key] == "entity":
			shape = "ellipse"
			fillcolor = "khaki1"
	file.write(nodeTemplate % (key,nodeLabel,shape,fillcolor))
# Build Edge Statement
for key in edge:
	item = edge[key]
	if key in label:
		itemLabel = "%s\\ntype:%s" %(label[key],item['type'])
	else:
		itemLabel = "type:%s" %item['type']
	file.write(edgeTemplate %(item['from'],item['to'],itemLabel))
file.write("}")
file.close()

