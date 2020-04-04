#!/usr/bin/python
"""A script for parsing 800-53 control dependencies

Run from project root.
Assumes data files are in data/dependencies

usage: python lib/parsedependencies.py

"""
import re
import os
import sys
import pprint

sys.path.append(os.path.join('lib'))
sys.path.append(os.path.join('data'))
from seccontrol import SecControl

# Config
base_path = "./"
dep_dir = "data/dependencies/"
out_dir = ""

log_dir = "./"
# tmp_dir = "sandbox/tmp/"

# Change these for a given run
input_path = base_path + dep_dir
output_path = base_path + out_dir

# Functions

def read_file_into_array(file, delimiter="\n"):
	"""Returns contents of file in array split on the splitter text
	
	# Example
	lines = read_file_into_array(filepath, "\n")
	"""
	try:
		f = open(file)
		t = f.read()
		f.close()
		lines = t.split(delimiter)
		return lines
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise
	else:
		return False

def write_array_into_file(text_array, file, delimiter="\n" ):
	try:
		# change this to append...
		f = open(file, "w")
		f.write(delimiter.join(text_array))
		f.close()
		return file
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise
	else:
		return False

def showEdges(graph, node):
	if node in graph:
		print "%s edges: %s" % (node, graph[node])
	else:
		print "%s not found in graph" % (node)

def dep_resolve(graph, node, resolved):
	if node in graph:
		# print node 
		sc = SecControl(node)
		print "%s - %s (%s)" % (node, sc.title, sc.responsible)
		# print "      edgees: %s" % (graph[node])
		for edge in graph[node]:
			if edge not in resolved:
				dep_resolve(graph, edge, resolved)
			resolved.append(node)
	else:
		print "%s not found in graph" % (node)

def precursor_graph(graph, node, resolved):
	# print node
	# print "precursors: ", graph[node]
	print node, ": ", graph[node]
	tup = tuple((precursor, node) for precursor in graph[node])
	resolved.append(node)
	# print "tup->list ", node, list(tup)
	if len(list(tup)) > 0:
		print list(tup)
	for precursor in graph[node]:
		if precursor not in resolved:
			precursor_graph(graph, precursor, resolved)

def precursor_list(graph, node, resolved):
	if node in graph:
		if node not in resolved:
			resolved.append(node)
			for precursor in graph[node]:
				precursor_list(graph, precursor, resolved)

def precursor_edges(graph, node, edges):
	if node in graph:
		tup = tuple((precursor, node) for precursor in graph[node])
		for edge in list(tup):
			edges.append(edge)

# Main
# read list of files
files = os.listdir(input_path)
# print files

dep_dict = {}

for file in files:
	if file.endswith(".txt"):
		lines = read_file_into_array(input_path+file, "\n")
		# reset question_id and text_buffer to blank, index 0 holds matched codes
		text_buffer = ["0-0"]
		# print "\n=============="
		# print file
		# print lines[0:2]
		# print ""
		for line in lines:
			dep_list = line.split(" : ")
			# print dep_list

			# optionally filter for relationship 
			if dep_list[1] == 'precursor':
				for control in dep_list[2].split(","):
					d = dep_list[0].strip()
					r = dep_list[1].strip()
					u = control.strip()
					# print '"%s", "%s", "%s"' % (u, r, d)

					if u not in dep_dict.keys():
						dep_dict[u] = []
					
					if u == "None":
						continue
					# print '"%s" -> "%s"' % (u, d)

					if d in dep_dict.keys():
						dep_dict[d].append(u)
					else:
						dep_dict[d] = []
						dep_dict[d].append(u)
					# print "%s dependencies are: %s" % (d, dep_dict[d])


print "\n ====== Dependency graph loaded ========\n"

# resolved = []
# showEdges(dep_dict, "CA-5")
# resolved = []
# showEdges(dep_dict, "CA-2")

# print " "
# resolved = []
# dep_resolve(dep_dict, "CA-2", resolved)
# print "Resolve ", "AU-4"
# resolved = []
# dep_resolve(dep_dict, "AU-4", resolved)

if __name__ == "__main__":
    while (1==1):
		control_input = raw_input("Resolve which control? ")
		if control_input == "q":
			exit()
		sc = SecControl(control_input)
		# print "%s - %s " % (sc.id, sc.title)
		print "===================================="
		print sc.id, ": ", dep_dict[sc.id]
		resolved = []
		# dep_resolve(dep_dict, sc.id, resolved)
		precursor_list(dep_dict, sc.id, resolved)
		print resolved
		edges = []
		for node in resolved:
			precursor_edges(dep_dict, node, edges)
		print edges

		print "    "



	
	