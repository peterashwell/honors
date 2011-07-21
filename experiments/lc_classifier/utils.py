import random
from math import fabs
from math import tan
from math import radians
from math import floor
from math import sqrt
import numpy

# Take the average of the two nearest values that are present to position
def simple_interpolate(lc):
	max_length = int(lc[0][-1])
	new_lc = [[], []]
	# Iterato over all time indices that should be there 
	available_index = 0 # The index of the available time
	for time in xrange(max_length):
		#if available_index >= len(lc[0]):
		#	new_lc[1].append((lc[1][available_index - 1] + 0) / 2.0)
		if time == lc[0][available_index]:
			new_lc[0].append(time)
			new_lc[1].append(lc[1][available_index])
			available_index += 1
		else: # Interpolate
			if available_index == 0 or available_index == lc[0][-1]:
				pass
			else:
				new_lc[0].append(time)
				new_lc[1].append((lc[1][available_index - 1] + lc[1][available_index]) / 2.0)
	return new_lc

def distribute(lc):
	flux = lc[1]
	min = 1
	max = 10
	new_flux = random.uniform(max ** -2.3, min) ** (1 / -2.3)
	mean = 1.0 * sum(flux) / len(flux)
	for obs_num in xrange(len(flux)):
		flux[obs_num] *= new_flux / mean
	return [lc[0], flux]

# Make percent of the signal available
def available(lc, percent):
	print percent, percent > 0, percent < 100
	assert percent > 0 and percent < 100
	#print percent
	#print len(lc[0])
	#print percent / 100.0
	#print floor(len(lc[0]) * (percent / 100.0))
	avail_range = int(floor(len(lc[0]) * (percent / 100.0)))
	return [lc[0][:avail_range], lc[1][:avail_range]]

# Add gaussian noise to the signal to the new signal to noise ratio
def signal_noise(lc, sig_noise_ratio):
	# First compute signal std dev
	lc_len = len(lc[0]) * 1.0
	sigma = sqrt(sum([x ** 2 for x in lc[1]]) / lc_len - (sum(lc[1]) / lc_len) ** 2)
	print sigma

	# Add random noise
	noise_amt = (1.0 / sig_noise_ratio) * sigma
	return [lc[0], [x + numpy.random.normal(0,noise_amt) for x in lc[1]]]

# Remove part of the signal as chunks of size 1, 2, 5
def gapify(lc, gap_amt):
	print lc[0]
	MINIMUM_POINTS = 5
	gaps = []
	time = lc[0]
	flux = lc[1]
	remove_amt = int(floor(len(flux) * gap_amt / 100.0))
	if len(lc[0]) - remove_amt < MINIMUM_POINTS:
		remove_amt = len(lc[0]) - MINIMUM_POINTS
	removed = 0
	while removed < remove_amt:
		gap_size = random.choice([1, 2, 5])
		if gap_size > remove_amt - removed:
			gap_size = remove_amt - removed
		removed += gap_size
		gap_start = random.randrange(1, len(flux) - gap_size)
		gaps.append((gap_start, time[gap_start:gap_start + gap_size]))
		time = time[:gap_start] + time[gap_start + gap_size:]
		flux = flux[:gap_start] + flux[gap_start + gap_size:]
	# reintroduce gaps as '-'
	for gap in reversed(gaps):
		start = gap[0]
		time = time[:start] + gap[1] + time[start:]
		flux = flux[:start] + ['-'] * len(gap[1]) + flux[start:] 
	return [time, flux]	

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
			#print interval_points
			#print gradient
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

# Change the intensity of the curve to have mean of new_mean
def normalise(lc, new_mean=1):
	# Compute mean of the curve
	flux_sum = 0
	for p in lc[1]:
		flux_sum += p
	flux_mean = flux_sum / (1.0 * len(lc[1]))
	# Update the flux measurements
	for i in xrange(len(lc[1])):
		lc[1][i] = lc[1][i] / flux_mean * new_mean
	return lc

def crossfold(folds, dataset):
	random.shuffle(dataset)
	fold_size = len(dataset) / folds
	fold_left = len(dataset) % folds
	#print "fold size:", fold_size
	#print "fold left:", fold_left
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

# In place, take a sample of maxlen of a light curve
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

def all_distortions(lc, noise, available_pct, missing, powlaw):
	if powerlaw:
		lc = distribute(lc)
	else:
		lc = normalise(lc)
	if noise > 0:
		lc = signal_noise(lc, noise)
	if available_pct < 100.0:
		lc = available(lc, available_pct)
	if missing > 0:
		lc = gapify(lc, missing)
	return lc
		
