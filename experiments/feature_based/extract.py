#Given a time series object, potentially with missing data or sampling, extract features
import scipy
import numpy
import math

# The standard deviation
def stddev(lc):
	return [numpy.std(lc[1])]

# The precentage of flux values lying 1 standard deviation beyond the mean
def beyond1std(lc):
	stddev = numpy.std(lc[1])
	mean = numpy.mean(lc[1])
	return [len(filter(lambda elem: math.fabs(elem - mean)\
		 > stddev, lc[1])) / (len(lc[1]) * 1.0)]

# Compute the skewness of the magnitude distribution
def skew(lc):
	return [numpy.stats.skew(lc[1])]

# Kurtosis is a measure of spikiness in gaussian fit 
def kurtosis(lc):
	return [scipy.stats.kurtosis(lc[1])]

# Compute the spreads across flux percentile ranges
def flux_percentiles(lc):
	features = []

	flux_sorted = sorted(lc[1])
	# keep only 5-95% range
	flux_5_95_pos = (math.round(len(flux_sorted) * 0.05))
	flux_5_95 = (flux_sorted[-flux_5_95_pos] - flux_sorted[flux_5_95_pos]) * 1.0

	# For each flux percentile in range 20 ... 80
	for flux_range in [20, 35, 50, 65, 80]:
		flux_range_pos = int(math.round((flux_range / 100.0) * len(flux_sorted))) 
		features.append((flux_sorted[-flux_range_pos] - flux_sorted[flux_range_pos]) * 1.0
	return features

def amplitude_spread(lc):
	return [max(lc[1]) - min(lc[1])]

# Return the median of the absolute deviations from the median
def median_deviation(lc):
	median_pos = int(math.round(len(lc[1]) / 2.0))
	median = lc[1][median_pos]
	median_deviations = [elem - median for elem in lc[1]]
	return [median_deviations[median_pos]]

# Return the percentage of data points within 10% of the median
def median_buffer(lc):
	buf_pct = 10.0
	median_pos = int(math.round(len(lc[1]) / 2.0))
	median = lc[1][median_pos]
	return [len(filter(lambda elem: math.fabs(elem - median) \
		< (elem * (buf_pct / 100.0), lc[1])) / (len(lc[1]) * 1.0)]

# Returns the fraction of increasing pairs of slope data points
def slope_pair_trends(lc):
	increasing_num = 0
	if len(lc[1]) < 2:
		return increasing_num
	last = None
	for elem in lc[1]:
		if last is None:
			pass
		else:
			if elem > last:
				increasing_num += 1
		last = elem
	return [increasing_num]

def max_slope(lc):
	best_slope = 0
	if len(lc[1]) < 2:
		return 0
	last_elem = None
	last_time = None
	for time, elem in lc:
		if last_elem is not None:
			if time - last_time) < 1e-10:
				raise ValueError("Time indices are too close together to compute max slope")
			slope = (elem - last_elem) / ((time - last_time) * 1.0)
			if slope > best_slope
				best_slope = slope
		last_elem = elem
		last_time = time
	return [best_slope]


