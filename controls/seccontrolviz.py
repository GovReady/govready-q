#!/usr/bin/python
"""A script for parsing 800-53 control dependencies

Run from project root.
Assumes data files are in data/dependencies

usage: python lib/viz_control_precursor.py

"""

__author__ = "Greg Elin (gregelin@gitmachines.com)"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2015/08/05 6:02:00 $"
__copyright__ = "Copyright (c) 2015 GovReady PBC"
__license__ = "GPL 3.0"

import re
import os
import sys
import pprint
import graphviz as gv

sys.path.append(os.path.join('lib'))
sys.path.append(os.path.join('data'))
from seccontrol import SecControl

import functools

class SecControlViz(object):
	"visualize 800-53 security controls"
	def __init__(self, id, vizformat='svg'):
		self.id = id
		# Config
		self.base_path = "./"
		self.dep_dir = "data/dependencies/"
		self.out_dir = ""
		self.log_dir = "./"
		# graphviz image format
		self.vizformat = vizformat
		self.width = 2.5
		self.height = 2.5
		self.graph = functools.partial(gv.Graph, format=self.vizformat)
		self.digraph = functools.partial(gv.Digraph, format=self.vizformat)

		# Change these for a given run
		self.input_path = self.base_path + self.dep_dir
		self.output_path = self.base_path + self.out_dir

		# load graph
		self.dep_dict = self._load_graph_from_dependency_files()

		# load other 
		self.resolved = []
		self.nodes = []
		self.edges = []

	def _load_graph_from_dependency_files(self):
		"load graph from reading dependency files"
		# # read list of files
		files = os.listdir(self.input_path)
		# print files

		dep_dict = {}

		for file in files:
			if file.endswith(".txt"):
				lines = self.read_file_into_array(self.input_path+file, "\n")
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
		return dep_dict

	def read_file_into_array(self, file, delimiter="\n"):
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

	def add_nodes(self, graph, nodes):
		for n in nodes:
			if isinstance(n, tuple):
				graph.node(n[0], **n[1])
			else:
				graph.node(n)
		return graph

	def add_edges(self, graph, edges):
		for e in edges:
			if isinstance(e[0], tuple):
				graph.edge(*e[0], **e[1])
			else:
				graph.edge(*e)
		return graph

	def write_array_into_file(self, text_array, file, delimiter="\n" ):
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

	def node_options_by_id(self, node):
		""" return options for single node id """
		# Pass in options to method
		options = {}
		sc = SecControl(node)
		sc_title = sc.title
		options['label'] = "%s\n%s" % (node, sc_title.title())
		options['shape'] = "egg"
		options['fontname'] = "arial"
		options['fontsize'] = "12"
		# options['fontcolor'] = "blue"
		# tooltip and clickable URL links (svg)
		options['tooltip'] = "(%s) %s" % (node, sc.title.title())
		options['URL'] = "/control?id=%s" % sc.id
		# color code by responsibility
		options['fontcolor'] = {'organization': 'cornflowerblue', 'information system': 'palevioletred', 'withdrawn': 'gray'}[sc.responsible]
		options['color'] = {'organization': 'cornflowerblue', 'information system': 'palevioletred', 'withdrawn': 'gray'}[sc.responsible]
		return options

	def node_options_tuples(self, nodes):
		""" convert simple array of nodes to node tuples having options """
		tup = tuple((node, self.node_options_by_id(node)) for node in nodes)
		return list(tup)

	def showEdges(self, graph, node):
		if node in graph:
			print "%s edges: %s" % (node, graph[node])
		else:
			print "%s not found in graph" % (node)

	def dep_resolve(self, graph, node, resolved):
		if node in graph:
			# print node 
			sc = SecControl(node)
			# print "%s - %s (%s)" % (node, sc.title, sc.responsible)
			# print "      edgees: %s" % (graph[node])
			for edge in graph[node]:
				if edge not in resolved:
					self.dep_resolve(graph, edge, resolved)
				self.resolved.append(node)
		else:
			print "%s not found in graph" % (node)

	def precursor_graph(self, graph, node, resolved):
		# print node
		# print "precursors: ", graph[node]
		# print node, ": ", graph[node]
		tup = tuple((precursor, node) for precursor in graph[node])
		resolved.append(node)
		if len(list(tup)) > 0:
			print list(tup)
		for precursor in graph[node]:
			if precursor not in resolved:
				precursor_graph(graph, precursor, resolved)

	def precursor_list(self, graph, node, resolved):
		""" recursive function to sets self.nodes to have list of precursor nodes (e.g, dependencies) """
		if node in graph:
			if node not in resolved:
				resolved.append(node)
				for precursor in graph[node]:
					self.precursor_list(graph, precursor, resolved)

	def precursor_edges(self, graph, node, edges):
		if node in graph:
			tup = tuple(((precursor, node), {'color': 'darkkhaki', 'arrowhead': 'open'}) for precursor in graph[node])
			for edge in list(tup):
				edges.append(edge)


	def set_image_size(self, width, height):
		""" set graph size in inches """
		self.width = width
		self.height = height

