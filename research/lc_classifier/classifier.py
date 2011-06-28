import psyco
psyco.full()
from operator import itemgetter
from utils import sample
from utils import normalise
from utils import distribute

class lcClassifier:
	def __init__(self, distance_fn, testdir):
		self._distance_fn = distance_fn
		self._testdir = testdir

	def nn_classify(self, N, test_lc, train_files):
		best_matches = []
		best_distances = []
		best_files = []
		# Read index of each lc file
		upto = 0
		for filename in train_files:
			#if upto % 200 == 0:
			#	print upto
			upto += 1
			# Read all the light curve data into an array
			lc_data = open(self._testdir + '/' + filename)
			
			lc_class = filename.strip().split('_')[0]
			lc = [[], []]
			for line in lc_data:
				line = line.strip().split(',')
				lc[0].append(float(line[0]))
				lc[1].append(float(line[1]))
			lc_data.close()
			normalise(lc)
			lc = sample(lc, 400)			
			lc = distribute(lc)
			# Update the nearest neighbour
			distance = self._distance_fn(test_lc, lc)
		
			# Find insert point
			
			insert_point = 0
			found = False
			for insert_point, bd in enumerate(best_distances):
				if bd >= distance:
					found = True
					break
			if found or len(best_distances) == 0:
				best_distances.insert(insert_point, distance)
				best_matches.insert(insert_point, lc_class)
				best_files.insert(insert_point, filename)
			# Pop from the top of the list if it's too long
			if len(best_distances) > N:
				best_distances.pop()
				best_matches.pop()
				best_files.pop()
		
		# Compute nearest neighbor by majority
		near_count = {}
		for c in best_matches:
			if c not in near_count.keys():
				near_count[c] = 1
			else:
				near_count[c] += 1
		#print sorted(near_count.items(), key=itemgetter(1))
		return [sorted(near_count.items(), key=itemgetter(1))[-1][0], best_files]
