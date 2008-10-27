#!/usr/bin/env python

from __future__ import division

from pylab import *
from numpy import *
import numpy

class Tc:
	"""
	Taylor coefficients Tc.
	One can propagate more than one direction at a time (called vector mode) by initializing with
	mytc = Tc(x0, [[x11,...,x1Ndir],
	               [x21,...,x2Ndir],
		            ....
		           [xD1,...,xDNdir]])
		       
	For convenience it is also possible to initialize with
	mytc = Tc([x0,x1,...,xD])
	i.e. only propagating one direction at a time.
	"""
	def __init__(self,in_t0,tc=None):
		if tc == None:
			self.t0 = in_t0[0]
			self.tc = asarray(in_t0[1:])
		else:	
			self.t0 = in_t0
			self.tc = asarray(tc)
	
	def copy(self):
		return Tc(self.t0, self.tc.copy())
	
	def set_zero(self):
		self.t0 = 0.
		self.tc[:] = 0
		return self

	def __add__(self,rhs):
		return Tc(self.t0 + rhs.t0, self.tc[:] + rhs.tc[:])
	
	def __mul__(self,rhs):
		#print 'shape(self.tc)',shape(self.tc)
		#print 'shape(rhs.tc)',shape(rhs.tc)
		#print 'self.tc=',self.tc
		#print 'rhs.tc=',rhs.tc
		#d=2
		#print 'self.tc[:d]',self.tc[:d-1]
		#print 'rhs.tc[d-2::-1]',rhs.tc[d-2::-1]
		#print 'self.tc[:d-1] * rhs.tc[d-2::-1]', self.t0*rhs.tc[d-1] +  self.tc[:d-1] * rhs.tc[d-2::-1] + self.tc[d-1] * rhs.t0
		#exit()
		
		def middle_taylor_series(d):
			if d>1:
				return 	npy.sum(self.tc[:d-1] * rhs.tc[d-2::-1], axis = 0)
			return 0
		
		D = shape(self.tc)[0]
		E = shape(rhs.tc)[0]
		assert D==E
		return Tc(self.t0 * rhs.t0,
					 npy.array(  [ self.t0*rhs.tc[d-1] + middle_taylor_series(d)  + self.tc[d-1] * rhs.t0 for d in range(1,D+1)]
					))

	def __str__(self):
		return 'Tc(%s,%s)'%(str(self.t0),str(self.tc))

class Function:
	def __init__(self, args, function_type='var'):
		if function_type == 'var':
			self.type = 'var'
		elif function_type == 'id':
			self.type = 'id'
		elif function_type == 'add':
			self.type = 'add'
		elif function_type == 'mul':
			self.type = 'mul'
		else:
			raise NotImplementedError('function_type must be either \'v\' or \'mul\' or  \'add\'')

		self.args = args
		self.x = self.eval()
		self.xbar = self.x.copy().set_zero()
		self.id = self.cgraph.functionCount
		self.cgraph.functionCount += 1
		self.cgraph.functionList.append(self)


	def as_function(self, in_x):
		if not isinstance(in_x, Function):
			fun = Function(self.x.copy().set_zero())
			fun.x.t0 = in_x
			return fun
		return in_x
		
		
	def __add__(self,rhs):
		rhs = self.as_function(rhs)
		return Function([self, rhs], function_type='add')

	def __mul__(self,rhs):
		rhs = self.as_function(rhs)
		return Function([self, rhs], function_type='mul')	

	def __radd__(self,lhs):
		return self + lhs

	def __rmul__(self,lhs):
		return self * lhs
	
	def __str__(self):
		try:
			ret = '%s%s:(x=%s)(xbar=%s)'%(self.type,str(self.id),str(self.x),str(self.xbar))
		except:
			ret = '%s%s:(x=%s)'%(self.type,str(self.id),str(self.x))
		return ret
	
	def __repr__(self):
		return self.__str__()

	def eval(self):
		if self.type == 'var':
			return self.args
		
		elif self.type == 'add':
			return self.args[0].x + self.args[1].x

		elif self.type == 'mul':
			return self.args[0].x * self.args[1].x

	def reval(self):
		if self.type == 'var':
			pass


		elif self.type == 'add':
			self.args[0].xbar += self.xbar
			self.args[1].xbar += self.xbar

		elif self.type == 'mul':
			self.args[0].xbar += self.xbar * self.args[1].x
			self.args[1].xbar += self.xbar * self.args[0].x


class CGraph:
	"""
	We implement the Computational Graph (CG) as Directed Graph
	The Graph of y = x1(x2+x3) looks like

	--- independent variables
	v1(x1): None
	v2(x2): None
	v3(x3): None

	--- function operations
	+4(v2.x + v3.x): [v2,v3] 
	*5(v1.x * +4.x): [v1,+4]

	--- dependent variables
	v6(*5.x): [*5]
	
	"""
	
	def __init__(self):
		self.functionCount = 0
		self.functionList = []
		self.dependentFunctionList = []
		self.independentFunctionList = []
		Function.cgraph = self

	def __str__(self):
		return 'vertices:\n' + str(self.functionList)

	def forward(self,x):
		# populate independent arguments with new values
		for nf,f in enumerate(self.independentFunctionList):
			f.args = x[nf]
			
		# traverse the computational tree
		for f in self.functionList:
			f.x = f.eval()

	def reverse(self,xbar):
		for nf,f in enumerate(self.dependentFunctionList):
			f.xbar = xbar[nf]

		for f in self.functionList[::-1]:
			f.reval()

def tape(f,in_x):
	x = in_x.copy()
	N = size(x)
	cg = CGraph()
	ax = numpy.array([Function(Tc([x[n]])) for n in range(N)])
	cg.independentFunctionList = ax
	ay = f(ax)

	cg.dependentFunctionList = numpy.array([ay])
	return cg

def gradient_from_graph(cg,x=None):
	if x != None:
		cg.forward(x)
	cg.reverse(numpy.array([Tc([1.])]))
	N = size(cg.independentFunctionList)
	return numpy.array([cg.independentFunctionList[n].xbar.t0 for n in range(N)])

def gradient(f, in_x):
	cg = tape(f,in_x)
	return gradient_from_graph(cg)

def hessian(f, in_x):
	x = in_x.copy()
	N = size(x)
	cg = CGraph()
	Id = eye(N).tolist()
	ax = numpy.array([Function(Tc(x[n], [Id[n]])) for n in range(N)])
	cg.independentFunctionList = ax
	ay = f(ax)
	cg.dependentFunctionList = numpy.array([ay])
	cg.reverse(numpy.array([Tc(1.,[[0. for n in range(N)]])]))
	
	H = numpy.zeros((N,N),dtype=float)
	for r in range(N):
		H[r,:] = ax[r].xbar.tc
			
	return H


if __name__ == "__main__":

	## Test on Taylor Coefficients
	#x = Tc([11.,1.])
	#y = Tc([13.,1.])
	#print x+y
	#print x*y
	
	#x = Tc([11.])
	#y = Tc([13.])
	#print x+y
	#print x*y
		
		
	## Test for Reverse Mode
	
	#cg = CGraph()
	#x = Function(Tc([11.,1.]))
	#y = Function(Tc([13.,1.]))
	
	#z = x * y 

	#cg.independentFunctionList = [x,y]
	#cg.dependentFunctionList = [z]
	#cg.forward([Tc([11.,0.]), Tc([13.,1.])])
	#print z
	#cg.reverse([Tc([1.,0.])])
	#print x.xbar
	#print y.xbar

	#def f(x):
		#return 2*x[0]*x[1] + 1.
	#x = array([11.,13.])
	#cg = tape(f,x)
	#print cg
	#gradient_from_graph(cg)
	#print cg
	#print gradient(f,x)


	#N = 10
	#A = 0.125 * numpy.eye(N)
	#x = numpy.ones(N)

	#def f(x):
		#return 0.5*numpy.dot(x, numpy.dot(A,x))


	## normal function evaluation
	#y = f(x)

	## taping + reverse evaluation
	#g_reverse = gradient(f,x)

	#print g_reverse

	##taping
	#cg = tape(f,x)
	#print gradient_from_graph(cg)

	#cg.plot()
	
	
	# Test vector forward mode
	#x = Tc(3.,[[1.,1.,0.],[0.,0.,0.]])
	#y = Tc(4.,[[0.,1.,1.],[0.,0.,0.]])
	
	#print 'x+y=',x+y
	#print 'x*y=',x*y
	
	# Test hessian
	def f(x):
		return x[1]*x[0]
	x = array([11.,13.])	
	print hessian(f,x)
	
	N = 6
	A = 13.1234 * numpy.eye(N) + numpy.ones((N,N))
	x = numpy.ones(N)

	def f(x):
		return 0.5*numpy.dot(x, numpy.dot(A,x))
	
	print hessian(f,x)

