#!/usr/bin/env python

from pylab import *
from numpy import  *
from forward_mode  import *

def f_smooth(x):
	"""function"""
	return sin(x) + 0.01*(x-100)**2

def g_smooth(x):
	"""gradient"""
	return cos(x) + 0.03*(x-100)

def wolfe_function(x):
	if x[0]>=abs(x[1]):
		return 5*sqrt(9*x[0]**2 + 16*x[1]**2)
	elif 0 < x[0] and x[0] < abs(x[1]):
		return 9*x[0] + 16 * abs(x[1])
	elif x[0]<=0:
		return 9*x[0]+16*abs(x[1]) - x[0]**9
	else:
		print 'x[0]=',x[0], 'oh screw that'

def wolfe_gradient(x,alpha=5.):
	return gradient(wolfe_function,x)

def rosenbock_function(x,alpha=5.):
	return alpha * (x[1] - x[0]**2)**2 +  (1. - x[0])**2
def rosenbock_gradient(x,alpha=5.):
	return gradient(rosenbock_function,x)

def square_function(x):
	return 10*x[0]**2 + x[1]**2
def square_gradient(x):
	return array([20*x[0], 2*x[1]])

def steepest_descent(ffcn,gfcn, x, epsilon = 10**-4, delta = 10**-4, sigma= 10**-1, beta = 10 ):
	"""
		INPUT: ffcn			objective function
		INPUT: gfcn 		gradient of the objective function
		INPUT: sigma		not too large parameter
		INPUT: beta		not too small parameter
	"""
	def backtracking_linesearch(g,x,s):
		"""
		backtracking with alpha_plus = minimizer of quadratic interpolating polynomial
		INPUT: g		gradient of f at x as array
		INPUT: x		starting point
		INPUT: s		search direction
		OUTPUT: alpha	step length
		"""
		def q(alpha):
			if abs(alpha) < 0.00001 : # should be replaced with an almost equal check!!
				return 1
			return (ffcn(x + alpha*s) - ffcn(x))/(alpha * dot(g,s))

		# double alpha until  sigma > q_k(alpha)
		alpha = 1.
		
		while q(alpha) >= sigma:
			alpha = alpha * 2
			#print 'q(alpha)',q(alpha),alpha
		# backtracking
		i = 0
		while q(alpha)< sigma and i < 500:
			#alpha_plus = 0.9 * alpha
			alpha_plus = alpha / ( 2.* ( 1- q(alpha)))
			alpha = max(1./beta * alpha, alpha_plus)
			#print q(alpha),alpha
			i+=1
		return alpha

	# repeating the linesearch
	x_old = inf
	g = inf
	i = 0
	while norm(g) > epsilon and norm(x_old - x) > delta and i<500:
		# STEP 1: compute the gradient
		g = gfcn(x)
		# STEP 2: perform line search
		s = -g
		alpha = backtracking_linesearch(g,x,s)
		x_old = x
		print '\n\n\nx coord=', x
		print 'search direction s=',s
		print 'step multiplier alpha=',alpha
		print 'objective function f(x)=', ffcn(x)
		plot([x[0]], [x[1]], 'ro')
		text(x[0], x[1], '%d'%i)
		i+=1
		x = x+alpha*s

	return x


if __name__ == "__main__":
	# plot the contours
	xmin = -1.5; xmax = 6; ymin = -4; ymax=4;
	x = linspace(xmin,xmax,100)
	y =  linspace(ymin,ymax,100)
	n = shape(x)[0]
	z = zeros((n,n))
	for i in range(n):
		for j in range(n):
			z[j,i] = wolfe_function(array([x[i], y[j]]))
	contour(z, origin='lower', extent=[xmin,xmax,ymin,ymax])
	colorbar()
	
	x = array([5,-4],dtype=float)


	#figure()
	#x_star = steepest_descent(square_function, square_gradient, x)
	#x_star = steepest_descent(rosenbock_function, rosenbock_gradient, x)
	x_star = steepest_descent(wolfe_function, wolfe_gradient, x)


	# 1D optimization
	#x = 0
	#x_star = steepest_descent(f_smooth, g_smooth, x)
	
	#print 'x_star =',x_star
	savefig('steepest_descent_on_rosenbrock_function.eps')
	show()
	

	
 