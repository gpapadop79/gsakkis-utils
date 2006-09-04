#Description:
#
#'sparse' is a matrix class based on a dictionary to store data using 2-element tuples (i,j)
#as keys (i is the row and j the column index). The common matrix operations such as 
#'dot' for the inner product, multiplication/division by a scalar, indexing/slicing, etc. are
#overloaded for convenience. When used in conjunction with the 'vector' class, 'dot'
#products also apply between matrics and vectors. Two methods, 'CGsolve' and 
#'biCGsolve', are provided to solve linear systems. Tested using Python 2.2.

#!/usr/bin/env python


import math, types, operator

"""
A sparse matrix class based on a dictionary, supporting matrix (dot)
product and a conjugate gradient solver. 

In this version, the sparse class inherits from the dictionary; this
requires Python 2.2 or later.
"""

class sparse(dict):
	"""
	A complex sparse matrix 
	A. Pletzer 5 Jan 00/12 April 2002

	Dictionary storage format { (i,j): value, ... }
	where (i,j) are the matrix indices
	"""

	# no c'tor

	def size(self):
		" returns # of rows and columns "
		nrow = 0
		ncol = 0
		for key in self.keys():
			nrow = max([nrow, key[0]+1])
			ncol = max([ncol, key[1]+1])
		return (nrow, ncol)

	def __add__(self, other):
		res = sparse(self.copy())
		for ij in other:
			res[ij] = self.get(ij,0.) + other[ij]
		return res
		
	def __neg__(self):
		return sparse(zip(self.keys(), map(operator.neg, self.values())))

	def __sub__(self, other):
		res = sparse(self.copy())
		for ij in other:
			res[ij] = self.get(ij,0.) - other[ij]
		return res
		
	def __mul__(self, other):
		" element by element multiplication: other can be scalar or sparse "
		try:
			# other is sparse
			nval = len(other)
			res = sparse()
			if nval < len(self):
				for ij in other:
					res[ij] = self.get(ij,0.)*other[ij]
			else:
				for ij in self:
					res[ij] = self[ij]*other.get(ij,0j)
			return res
		except:
			# other is scalar
			return sparse(zip(self.keys(), map(lambda x: x*other, self.values())))


	def __rmul__(self, other): return self.__mul__(other)

	def __div__(self, other):
		" element by element division self/other: other is scalar"
		return sparse(zip(self.keys(), map(lambda x: x/other, self.values())))
		
	def __rdiv__(self, other):
		" element by element division other/self: other is scalar"
		return sparse(zip(self.keys(), map(lambda x: other/x, self.values())))

	def abs(self):
		return sparse(zip(self.keys(), map(operator.abs, self.values())))

	def out(self):
		print '# (i, j) -- value'
		for k in self.keys():
			print k, self[k]

	def save(self, filename, OneBased=0):
		"""
		Save matrix in file <filaname> using format:
		OneBased, nrow, ncol, nnonzeros
		[ii, jj, data]
		"""
		m = n = 0
		nnz = len(self)
		for ij in self.keys():
			m = max(ij[0], m)
			n = max(ij[1], n)
		f = open(filename,'w')
		f.write('%d %d %d %d\n' % (OneBased, m+1,n+1,nnz))
		for ij in self.keys():
			i,j = ij
			f.write('%d %d %20.17f \n'% \
				(i+OneBased,j+OneBased,self[ij]))
		f.close()
				
###############################################################################

def isSparse(x):
    return hasattr(x,'__class__') and x.__class__ is sparse

def transp(a):
	" transpose "
	new = sparse({})
	for ij in a:
		new[(ij[1], ij[0])] = a[ij]
	return new

def dotDot(y,a,x):
	" double dot product y^+ *A*x "
	import vector
	if vector.isVector(y) and isSparse(a) and vector.isVector(x):
		res = 0.
		for ij in a.keys():
			i,j = ij
			res += y[i]*a[ij]*x[j]
		return res
	else:
		print 'sparse::Error: dotDot takes vector, sparse , vector as args'

def dot(a, b):
	" vector-matrix, matrix-vector or matrix-matrix product "
	import vector
	if isSparse(a) and vector.isVector(b):
		new = vector.zeros(a.size()[0])
		for ij in a.keys():
			new[ij[0]] += a[ij]* b[ij[1]]
		return new
	elif vector.isVector(a) and isSparse(b):
		new = vector.zeros(b.size()[1])
		for ij in b.keys():
			new[ij[1]] += a[ij[0]]* b[ij]
		return new
	elif isSparse(a) and isSparse(b):
		if a.size()[1] != b.size()[0]:
			print '**Warning shapes do not match in dot(sparse, sparse)'
		new = sparse({})
		n = min([a.size()[1], b.size()[0]])
		for i in range(a.size()[0]):
			for j in range(b.size()[1]):
				sum = 0.
				for k in range(n):
					sum += a.get((i,k),0.)*b.get((k,j),0.)
				if sum != 0.:
					new[(i,j)] = sum
		return new
	else:
		raise TypeError, 'in dot'

def diag(b):
	# given a sparse matrix b return its diagonal
	import vector
	res = vector.zeros(b.size()[0])
	for i in range(b.size()[0]):
		res[i] = b.get((i,i), 0.)
	return res
		
def identity(n):
	if type(n) != types.IntType:
		raise TypeError, ' in identity: # must be integer'
	else:
		new = sparse({})
		for i in range(n):
			new[(i,i)] = 1+0.
		return new

###############################################################################
if __name__ == "__main__":

	print 'a = sparse()'
	a = sparse()

	print 'a.__doc__=',a.__doc__

	print 'a[(0,0)] = 1.0'
	a[(0,0)] = 1.0
	a.out()

	print 'a[(2,3)] = 3.0'
	a[(2,3)] = 3.0
	a.out()

	print 'len(a)=',len(a)
	print 'a.size()=', a.size()
			
	b = sparse({(0,0):2.0, (0,1):1.0, (1,0):1.0, (1,1):2.0, (1,2):1.0, (2,1):1.0, (2,2):2.0})
	print 'a=', a
	print 'b=', b
	b.out()

	print 'a+b'
	c = a + b
	c.out()

	print '-a'
	c = -a
	c.out()
	a.out()

	print 'a-b'
	c = a - b
	c.out()

	print 'a*1.2'
	c = a*1.2
	c.out()


	print '1.2*a'
	c = 1.2*a
	c.out()
	print 'a=', a
	
	try:
		print 'dot(a, b)'
		print 'a.size()[1]=',a.size()[1],' b.size()[0]=', b.size()[0]
		c = dot(a, b)
		c.out()
	
		print 'dot(b, a)'
		print 'b.size()[1]=',b.size()[1],' a.size()[0]=', a.size()[0]
		c = dot(b, a)
		c.out()
	
		print 'dot(b, vector.vector([1,2,3]))'
		c = dot(b, vector.vector([1,2,3]))
		c.out()
	
		print 'dot(vector.vector([1,2,3]), b)'
		c = dot(vector.vector([1,2,3]), b)
		c.out()

		print 'b.size()=', b.size()
	except: pass
	
	print 'a*b -> element by element product'
	c = a*b
	c.out()

	print 'b*a -> element by element product'
	c = b*a
	c.out()
	
	print 'a/1.2'
	c = a/1.2
	c.out()

	print 'c = identity(4)'
	c = identity(4)
	c.out()

	print 'c = transp(a)'
	c = transp(a)
	c.out()


	b[(2,2)]=-10.0
	b[(2,0)]=+10.0

	try:
		import vector
		print 'Check conjugate gradient solver'
		s = vector.vector([1, 0, 0])
		print 's'
		s.out()
		x0 = s 
		print 'x = b.biCGsolve(x0, s, 1.0e-10, len(b)+1)'
		x = b.biCGsolve(x0, s, 1.0e-10,  len(b)+1)
		x.out()

		print 'check validity of CG'
		c = dot(b, x) - s
		c.out()
	except: pass

	print 'del b[(2,2)]'
	del b[(2,2)]

	print 'del a'
	del a
	#a.out()


#Discussion:
#
#I'm using this class in the context of a two-dimensional finite element code. 
#When discretized, the partial differential equation reduces to a sparse matrix
#system. Because 'sparse' stores the data in a dictionary, the size of the 
#problem need not be known before hand (the sparse matrix elements are filled up
#along the way). For such problems, the resulting matrix tends to be extremely 
#sparse so that there is little advantage in storing data contiguously in memory;
#the dictionary random based storage turns out to be appropriate. 
#
#'sparse' in conjunction with 'vector' (also available as a Python recipe) supports
#many matrix-vector operations (+, dot product etc) as well as elementwise operations
#(sin, cos, ...). Thus, in order to use 'sparse' you will need to download 
#'vector'. 'sparse' comes in addition with a method for solving linear matrix systems based
#on the conjugate gradient method.
#
#If you want a picture of your matrix using Tkinter, I suggest that you also download 
#'colormap'.
#
#Just type in 'python sparse.py' to test some of sparse's functionality.
#
#PS This version uses Python 2.2's new feature for deriving a class from a 
#dictionary type. It also runs significantly faster than the previously posted
#version, thanks to the use of map/reduce and lambda.
#
#--Alex.
 
