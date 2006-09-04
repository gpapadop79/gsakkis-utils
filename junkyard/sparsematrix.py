import math, types, operator

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

	#def __str__(self):
	#	return "\n".join(["%s %s k, self[k]
	#	for k,v in self.iteritems():
	#		print k, self[k]
	#
				
###############################################################################


def transpose(a):
	new = sparse({})
	for ij in a:
		new[(ij[1], ij[0])] = a[ij]
	return new

def dotDot(y,a,x):
	" double dot product y^+ *A*x "
	import vector
	if vector.isVector(y) and isinstance(a,sparse) and vector.isVector(x):
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
	if isinstance(a,sparse) and vector.isVector(b):
		new = vector.zeros(a.size()[0])
		for ij in a.keys():
			new[ij[0]] += a[ij]* b[ij[1]]
		return new
	elif vector.isVector(a) and isinstance(b,sparse):
		new = vector.zeros(b.size()[1])
		for ij in b.keys():
			new[ij[1]] += a[ij[0]]* b[ij]
		return new
	elif isinstance(a,sparse) and isinstance(b,sparse):
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

	print 'a[(0,0)] = 1.0'
	a[(0,0)] = 1.0
	print a

	print 'a[(2,3)] = 3.0'
	a[(2,3)] = 3.0
	print a

	print 'len(a)=',len(a)
	print 'a.size()=', a.size()
	import sys; sys.exit()
	
	b = sparse({(0,0):2.0, (0,1):1.0, (1,0):1.0, (1,1):2.0, (1,2):1.0, (2,1):1.0, (2,2):2.0})
	print 'a=', a
	print 'b=', b
	print b

	print 'a+b'
	c = a + b
	print c

	print '-a'
	c = -a
	print c
	print a

	print 'a-b'
	c = a - b
	print c

	print 'a*1.2'
	c = a*1.2
	print c


	print '1.2*a'
	c = 1.2*a
	print c
	print 'a=', a
	
	try:
		print 'dot(a, b)'
		print 'a.size()[1]=',a.size()[1],' b.size()[0]=', b.size()[0]
		c = dot(a, b)
		print c
	
		print 'dot(b, a)'
		print 'b.size()[1]=',b.size()[1],' a.size()[0]=', a.size()[0]
		c = dot(b, a)
		print c
	
		print 'dot(b, vector.vector([1,2,3]))'
		c = dot(b, vector.vector([1,2,3]))
		print c
	
		print 'dot(vector.vector([1,2,3]), b)'
		c = dot(vector.vector([1,2,3]), b)
		print c

		print 'b.size()=', b.size()
	except: pass
	
	print 'a*b -> element by element product'
	c = a*b
	print c

	print 'b*a -> element by element product'
	c = b*a
	print c
	
	print 'a/1.2'
	c = a/1.2
	print c

	print 'c = identity(4)'
	c = identity(4)
	print c

	print 'c = transpose(a)'
	c = transpose(a)
	print c


	b[(2,2)]=-10.0
	b[(2,0)]=+10.0

	try:
		import vector
		print 'Check conjugate gradient solver'
		s = vector.vector([1, 0, 0])
		print 's'
		print s
		x0 = s 
		print 'x = b.biCGsolve(x0, s, 1.0e-10, len(b)+1)'
		x = b.biCGsolve(x0, s, 1.0e-10,  len(b)+1)
		print x

		print 'check validity of CG'
		c = dot(b, x) - s
		print c
	except: pass

	print 'del b[(2,2)]'
	del b[(2,2)]


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
 
