from operator import itemgetter

class lcClassifier:
	def __init__(self, distance_fn):
		self._classes = classes
		self._distance_fn = distance_fn

	def nn_classify(self, N, test_lc, test_class, train_files):
		best_classes = []
		best_distances = []
		# Read index of each lc file
		for filename in train_files:
			# Read all the light curve data into an array
			lc_data = open(filename)
			lc = [[], []]
			for line in lc_data:
				line = line.strip().split(' ')
				lc[0].append(float(line[0]))
				lc[1].append(float(line[1]))
			lc_data.close()
			
			# Update the nearest neighbour
			distance = self.distance_fn(test_lc, lc)
			i = 0
			while distance < best_distances[i]::
				i += 1
			best_distances.insert(i, distance)
			best_matches.insert(i, test_class)
			
			# Pop from the top of the list if it's too long
			if len(best_distances) > N:
				best_distances.pop()
				best_matches.pop()
					
		# Compute nearest neighbor by majority
		near_count = {}
		for c in self.best_matches:
			if c not in near_count.keys():
				near_count[c] = 1
			else:
				near_count[c] += 1
		print sorted(near_count.items(), key=itemgetter(1))[0]
