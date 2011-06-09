import random
from math import fabs
from math import tan
from math import radians

# Find linear approximation of a light curve
def linearapprox(lc, granularity):
	approx = []
	interval_times = []
	interval_points = []
	for i, point in enumerate(lc[1]):
		interval_times.append(lc[0][i]) # grab time as well
		interval_points.append(point)
		if i != 0 and i % granularity == 0: # Compute linear regression
			S_xy = sum([x * y for x, y in zip(interval_times, interval_points)])
			S_x = sum(interval_times)
			S_y = sum(interval_points)
			S_xx = sum([x * x for x in interval_times])
			gradient = None
			if fabs(S_x + S_xx) < 1e-10:
				grad_symb = 0
			else:
				n = len(interval_times)
				gradient = (n * S_xy - S_x * S_y) / (n * S_xx - S_x ** 2)
				#print gradient, interval_points
			if gradient >= tan(radians(75)):
				grad_symb = 0
			elif gradient >= tan(radians(45)):
				grad_symb = 1
			elif gradient >= tan(radians(15)):
				grad_symb = 2
			elif gradient >= tan(radians(5)):
				grad_symb = 3
			elif gradient >= -1 * tan(radians(5)):
				grad_symb = 4 
			elif gradient >= -1 * tan(radians(15)):
				grad_symb = 5
			elif gradient >= -1 * tan(radians(45)):
				grad_symb = 6
			elif gradient >= -1 * tan(radians(75)):
				grad_symb = 7
			else: 
				grad_symb = 8
			approx.append([interval_times[0], interval_times[-1], grad_symb])
			interval_times = []
			interval_points = []
	return approx

def crossfold(folds, dataset):
	random.shuffle(dataset)
	fold_size = len(dataset) / folds
	fold_left = len(dataset) % folds
	print "fold size:", fold_size
	print "fold left:", fold_left
	# For each fold yield fold test and train
	prev_end = None # keep track of last endpoint for fold
	for fold_num in xrange(folds):
		if fold_left > 0:
			offset = 1
			fold_left -= 1
		else:
			offset = 0
		if prev_end is None: # first run
			fold_start = 0
			fold_end = 0 + fold_size + offset
			prev_end = fold_end
		else:
			fold_start = prev_end
			fold_end = fold_start + fold_size + offset
			prev_end = fold_end # record last endpoint
		
		test = dataset[fold_start : fold_end]
		train = dataset[:fold_start] + dataset[fold_end:]
		yield test, train

def sample(lc, maxlen):
	if len(lc[1]) <= maxlen:
		return lc
	else:
		new_lc = [[],[]]
		sparsity = int(len(lc[1]) / (1.0 * maxlen))
		#print "sparsity:", sparsity
		for i, point in enumerate(lc[1]):
			if i % sparsity == 0:
				new_lc[0].append(lc[0][i])
				new_lc[1].append(lc[1][i])
		return new_lc
