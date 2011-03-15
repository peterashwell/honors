import random

class BloTree:
	DIMENSION = 2
	LIMIT = 20
	def __init__(self, ):
		self.level = None
		self.data = []
		self.leaf = True
		self.split = None
		self.id = random.random()
		self.left = None
		self.right = None

	def tostring(self, indent):
		if self is None:
			return ''
		elif self.data is not None:
			return indent + str(self.id) + ' ' + str(self.data) + '\n'
		else:
			return self.left.tostring(indent + '\t') + \
			indent + '(' + str(self.level) + ' ' + str(self.id) + ' ' + str(self.split) + ')\n'\
			+ self.right.tostring(indent + '\t')
	
	def __repr__(self):
		return self.tostring('')
	
	# takes data as a tuple with [(d1, d2, ... , dLIMIT, other), (d1, d2, ..., )]
	def insert_all(self, data):
		
		if len(data) == 0:
			return # do nothing

		if len(data) <= self.LIMIT:
			#for item in data:
				#print item
				#if item[3] == 154470912:
				#	print "appears to have been added" 
			self.data = data
			self.leaf = True
			return

		if self.level == None:
			self.level = 0 # initialise root
		self.leaf = False
		self.data = None
		# find average of all data values
		sum = 0.0
		amount = 0.0
		for datum in data:
			amount += 1
			sum += datum[self.level]
		average = sum / amount
		self.split = average
		#if self.split == 0:
			#print "BALLBLAST", data
		for_left = []
		for_right = []
		#print "items: {} in: {}".format(len(data), 154470912 in [obj[3] for obj in data] )

		for datum in data:
			if datum[self.level] < self.split:
				for_left.append(datum)
				#if datum[3] == 154470912:
				#	print "going left, {} items".format(len(data))
			else:
				for_right.append(datum)
				#if datum[3] == 154470912:
					#print "going right, {} items".format(len(data))
		left = BloTree()
		right = BloTree()
		if len(for_left) == 0:
			left.leaf = True
			left.data = []
			self.left = left
			right.leaf = True
			right.data = for_right
			self.right = right
		elif len(for_right) == 0:
			right.leaf = True
			right.data = []
			self.right = right
			left.leaf = True
			left.data = for_left
			self.left = left
		else:
			left.level = (self.level + 1) % self.DIMENSION
			right.level = (self.level + 1) % self.DIMENSION
			self.left = left
			self.right = right
			self.left.insert_all(for_left)
			self.right.insert_all(for_right)
	
	def remove(self, item):
		if self is None:
			return # not in set
		elif self.leaf == True:
			#if item == 154470912:
				#print "ARGH"
			self.data.remove(item)
		else:
			if item[self.level] >= self.split:
				self.right.remove(item)
			else:
				self.left.remove(item) 

	def start_debug(self, id):
		return self.debug_search(id, "")
	
	def debug_search(self, id, path):
		#if path == "LRRRRLRL":
			#print "ASSBANDIT", self.data
		if self.leaf == True:
			#print "ASSBRAIN", self.data
			for elem in self.data:
				if elem[3] == id:
					#print "found at path", path
					return elem
		else:
			return self.left.debug_search(id, path + "L") \
			or self.right.debug_search(id, path + "R")
		return None

	def find_in_range(self, bounds):
		results = []
		self.rec_in_range(bounds, results, "")
		return results

	def rec_in_range(self, bounds, results, path):
		if self is None:
			return
		if self.leaf == True:
			check = False
			#if path == "LRRRRLRL":
				#print "at the path, self.data:", self.data
		#		check = True
				#print "BEFORE", self.data
				#print 154470912 in [obj[3] for obj in self.data]
				#3print self.data
				#print "DERPDER"
			#print "included path:", path
			for datum in self.data:
				in_range = True
				for d in xrange(self.DIMENSION):
					if datum[d] < bounds[d * 2] or \
						datum[d] > bounds[d * 2 + 1]:
						in_range = False
				if in_range:
					#print "accepted id", datum[3]
					results.append(datum)
				#else:
					#print bounds
					#print "rejected id:", datum
		#	if check:
		#		print "AFTER", 154470912 in [obj[3] for obj in results]
		#		print results
		else:
			low_bound = bounds[self.level * 2]
			high_bound = bounds[self.level * 2 + 1]
			if low_bound <= self.split: # include left
				if self.left is None:
					pass
					#print "ASSPLAY", self.right, self.leaf, self.split
				else:	
					self.left.rec_in_range(bounds, results, path + "L")
			if high_bound > self.split: # include right
				if self.right is None:
					pass
					#print "JIZZPLAY", self.left, self.leaf, self.split
				else:
					self.right.rec_in_range(bounds, results, path + "R")

		# TODO bounds as (d1_low, d1_high, d2_low, d2_high, ... etc)

#root = BloTree()
#root.insert_all([(180, 30, 's', 'f'), (186, 32), (188, 40), (190, 50), (187, 35), \
#(150, 25), (160, 20), (190, 34), (185, 35), (188.00001, 36), (189.9999999, 30), \
#(189, 40), (189, 32)])
#print root
#print "ass", root.find_in_range((188, 190, 30, 40))
#print root
