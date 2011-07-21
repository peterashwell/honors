#Given a time series object, potentially with missing data or sampling, extract features
import scipy
from scipy.stats import *
import numpy
import math
import lomb
from operator import itemgetter
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
	return [scipy.stats.skew(lc[1])]

# Kurtosis is a measure of spikiness in gaussian fit 
def kurtosis(lc):
	return [scipy.stats.kurtosis(lc[1])]

# Compute the spreads across flux percentile ranges
def flux_percentiles(lc):
	features = []

	flux_sorted = sorted(lc[1])
	# keep only 5-95% range
	flux_5_95_pos = int(round(len(flux_sorted) * 0.05))
	flux_5_95 = (flux_sorted[-flux_5_95_pos] - flux_sorted[flux_5_95_pos]) * 1.0

	# For each flux percentile in range 20 ... 80
	for flux_range in [10, 17.5, 25, 32.5, 40]:
		flux_range_pos = int(round((flux_range / 100.0) * len(flux_sorted))) 
		features.append((flux_sorted[-flux_range_pos] - flux_sorted[flux_range_pos]) * 1.0)
	return features

# Amplitude spread, normalised
def amplitude_spread(lc):
	return [max(lc[1]) - min(lc[1])]

# Return the median of the absolute deviations from the median
def median_deviation(lc):
	median_pos = int(round(len(lc[1]) / 2.0))
	median = lc[1][median_pos]
	median_deviations = [elem - median for elem in lc[1]]
	return [sorted(median_deviations)[median_pos]]

# Return the percentage of data points within 10% of the median
def median_buffer(lc):
	buf_pct = 10.0
	median_pos = int(round(len(lc[1]) / 2.0))
	median = lc[1][median_pos]
	return [len(filter(lambda elem: math.fabs(elem - median) \
		< (elem * (buf_pct / 100.0)), lc[1])) / (len(lc[1]) * 1.0)]

# Returns the fraction of increasing pairs of slope data points
def slope_pair_trends(lc):
	increasing_num = 0
	if len(lc[1]) < 2:
		return [increasing_num]
	last = None
	for elem in lc[1]:
		if last is None:
			pass
		else:
			if elem > last:
				increasing_num += 1
		last = elem
	return [increasing_num]

# Largest time-adjacent increase, normalised
def max_slope(lc):
	best_slope = 0
	if len(lc[1]) < 2:
		return [0]
	last_elem = None
	last_time = None
	for time, elem in zip(lc[0], lc[1]):
		if last_elem is not None:
			if math.fabs(time - last_time) < 1e-10:
				raise ValueError("Time indices are too close together to compute max slope")
			slope = (elem - last_elem) / ((time - last_time) * 1.0)
			if slope > best_slope:
				best_slope = slope
		last_elem = elem
		last_time = time
	return [best_slope]

def spectral_features(lc):
	FIND_FREQUENCIES = 4
	time = numpy.array(lc[0])
	flux = numpy.array(lc[1])
	# center the flux
	flux = (flux - numpy.mean(flux)) / (1.0 * numpy.std(flux))
	result = lomb.fasper(time, flux, 6.0, 6.0)
	# filter out weird frequencies
	spectral_results = filter(lambda elem: elem[0] < 0.55 and elem[0] > (2.0 / len(lc)), zip(result[0], result[1]))
	wavelengths = []
	for frequency in sorted(spectral_results, key=itemgetter(1), reverse=True):
		wavelength = int(round(1.0 / frequency[0]))
		# check if wavelength is approximately in array
		include = True
		for found_wavelength in wavelengths:
			if abs(found_wavelength - wavelength) <= 4:
				include = False
		if include:
			wavelengths.append(wavelength)
		if len(wavelengths) == FIND_FREQUENCIES:
			break
	if len(wavelengths) < FIND_FREQUENCIES:
		wavelengths += [0] * (FIND_FREQUENCIES - len(wavelengths))
	if len(wavelengths) < FIND_FREQUENCIES:
		wavelengths += [0] * (FIND_FREQUENCES - len(wavelengths))
	return wavelengths

def haar_recursive(flux):
	# assume list is power of two long
	averages = []
	differences = []
	for index in xrange(0, len(flux), 2):
		if flux[index] == '-' and flux[index + 1] == '-':
			average = '-'
			difference = '-'
		elif flux[index] == '-':
			average = flux[index + 1]
			difference = 0
		elif flux[index + 1] == '-':
			average = flux[index]
			difference = 0
		else:
			average = (flux[index] + flux[index + 1]) / 2.0
			difference = flux[index] - average
		averages.append(average)
		differences.append(difference)
	if len(averages) > 1:
		return haar_recursive(averages[:]) + differences
	else:
		return averages + differences

def haar_transform(lc):
	TOP_COEFFS = 8
	next_pow_2 = int(math.ceil(math.log(len(lc[0]), 2)))
	# arithmetical error...
	if 2 ** next_pow_2 < len(lc[0]):
		next_pow_2 += 1
	filled_lc = [lc[0][:], lc[1][:]]
#	start_time = int(lc[0][0])
#	end_time = int(start_time + 2 ** next_pow_2)
		
#	complete_time = range(start_time, end_time)
#	comp_position = 0
#	real_position = 0
# The curve should have '-' already for missing data
#	while comp_position < len(complete_time):
#		if comp_position >= len(lc[0]):
#			break
#		elif int(lc[0][real_position]) != complete_time[comp_position]: # missing
#			filled_lc[0].insert(comp_position, complete_time[comp_position])
#			filled_lc[1].insert(comp_position, '-')
#			comp_position += 1
#		else: # match (move to next real data point)
#			comp_position += 1
#			real_position += 1
	# fill out remainder of curve
	# doesn't matter that these time indices don't make sense (TODO make them make sense)
	remaining = 2 ** next_pow_2 - len(filled_lc[0])
	filled_lc[0] += range(int(lc[0][-1]) + 1, int(lc[0][-1]) + remaining + 1)
	filled_lc[1] += ['-'] * remaining
	
	transform = haar_recursive(filled_lc[1])
	# normalise the transformed haar spectra, and fill in missing data with 0s
	transform_avg = sum(filter(lambda elem: elem != '-', transform)) * 1.0
	norm_transform = []
	# replace missing data with 0 coefficient
	for item in transform:
		if item == '-':
			norm_transform.append(0)
		else:
			norm_transform.append(item / transform_avg)
	norm_transform = norm_transform[:TOP_COEFFS]
	if len(norm_transform) < TOP_COEFFS:
		norm_transform += [0] * (TOP_COEFFS - len(norm_transform))
	return norm_transform[:TOP_COEFFS] # return top 8 wavelet coefficients
