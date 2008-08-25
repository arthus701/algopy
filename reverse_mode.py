#!/usr/bin/env python

from pylab import *
from numpy import *
from networkx import *

class NodeType:
	var_node = 1
	add_node = 2


g = XDiGraph()
g.node_type = []

num_nodes = 0
#>>> G.add_edge(1,2)
#>>> G.add_node("spam")
class adouble:
	def __init__(self, x,dx):
		"""Constructor takes a list, array, tuple and variable lenght input"""
		global num_nodes

		self.x = x
		self.dx = dx
		self.index = num_nodes
		g.add_node(num_nodes)
		g.node_type.append( NodeType.var_node)
		num_nodes += 1

	def __add__(self, rhs):
		"""compute new Taylorseries of the function f(x,y) = x+y, where x and y adouble objects"""
		global num_nodes

		g.add_node(num_nodes)
		g.node_type.append( NodeType.add_node)
		num_nodes += 1
		g.add_edge(self.index, num_nodes)
		g.add_edge(rhs.index, num_nodes)

		retval = adouble(self.x + rhs.x, self.x * rhs.dx + self.dx *rhs.x)
		g.add_edge(num_nodes-2,  num_nodes-1)

		return retval


if __name__ == "__main__":
	x = adouble(1,0)
	y = adouble(2,0)
	z = x + y

	draw(g)
	show()
	
	
	
