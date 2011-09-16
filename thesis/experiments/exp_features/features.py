#Given a time series object, potentially with missing data or sampling, extract features
import scipy
from scipy.stats import *
import numpy
import math
from lightcurve import LightCurve
import lomb
from operator import itemgetter
from itertools import izip
import matplotlib.pyplot as plt

def flux_only(lc):
	# Centered and sorted flux to work with
	mean = numpy.mean(lc.flux)
	stddev = numpy.stddev(lc.flux)
	centered_flux = [(f - mean) / (1.0 * stddev) for f in lc.flux]
	sorted_flux = sorted(centered_flux)

	# Median
	median_pos = len(sorted_flux) / 2
	flux_median = sorted_flux[median_pos]
	
	# Median deviation
	median_deviations = [elem - flux_median for elem in lc.flux]
	flux_median_deviation = median_deviations[median_pos]

	# Skew
	flux_skew = scipy.skew(centered_flux)

	# Kurtosis
	flux_kurtosis = scipy.kurtosis(centered_flux)

	# Stuff for percentiles
	stddev = scipy.std(centered_flux) # is 1 but let's just do it again anyway
	mean = numpy.mean(centered_flux) # is 0 but we'll be explicit
	
	# Percentiles - one, fraction of data within regular inc * stddev from MEAN
	stddev_increments = [0.25, 0.5, 1, 1.5, 2, 3] # fractions of data lying within stddev * this
	median_percentiles = []
	for inc in stddev_increments:
		in_range = 0
		bound = sttdev * inc
		for f in centered_flux:
			if (math.fabs(f) - mean) < bound:
				in_range += 1
		median_percentiles.append((in_range * 1.0) / len(centered_flux))
	
	# Percentiles - two, spread of data within regular inc * stddev from MEDIAN
	stddev_increments = [0.25, 0.5, 1, 1.5, 2, 3] # fractions of data lying within stddev * this
	median_percentiles = []
	for inc in stddev_increments:
		in_range = 0
		bound = sttdev * inc
		for f in centered_flux:
			if (math.fabs(f) - flux_median) < bound:
				in_range += 1
		median_percentiles.append((in_range * 1.0) / len(centered_flux))

	# Maximum and minimum
	flux_max = max(centered_flux)
	flux_min = min(centered_flux) 
	
	return [flux_median, flux_median_devation, flux_skew, flux_kurtosis] + flux_mean_percentiles + \
	       flux_med_percentiles + [flux_max, flux_min]	


def flux_time(lc):
	
def spectral_features(lc):
	FIND_FREQUENCIES = 4
	time = numpy.array(lc.time)
	flux = numpy.array(lc.flux)
	# center the flux
	flux = (flux - numpy.mean(flux)) / (1.0 * numpy.std(flux))
	result = lomb.fasper(time, flux, 6.0, 6.0)
	# filter out weird frequencies
	spectral_results = filter(lambda elem: elem[0] < 0.55 and elem[0] > (2.0 / len(lc.time)), zip(result[0], result[1]))
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

def haar_coeffs(lc):
	TOP_COEFFS = 15
	next_pow_2 = int(math.ceil(math.log(len(lc.time), 2)))
	# arithmetical error...
	if 2 ** next_pow_2 < len(lc.time):
		next_pow_2 += 1
	filled_lc = LightCurve(lc.time[:], lc.flux[:])
	
	# fill out lc with blanks '-'
	remaining = 2 ** next_pow_2 - len(filled_lc.time)
	filled_lc.time += range(int(lc.time[-1]) + 1, int(lc.time[-1]) + remaining + 1)
	filled_lc.flux += ['-'] * remaining
	
	transform = haar_recursive(filled_lc.flux)
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

# return a list of linear segments of lc as (time, flux, time, flux) pairs
NUM_SEGS = 10
def linear_segmentation(lc):
	# Start with segments all adjoined
	segments = [[i, i+1] for i in xrange(len(lc.time) - 1)]
	# Compute cost in terms of least-squared
	costs = []
	current = segments[0]
	for next in segments[1:]:
		# Compute the cost of the merged segment and store in "costs"
		seg_indices = range(current[1], next[-1] + 1)
		seg_times = [lc.time[i] for i in seg_indices]
		seg_flux = [lc.flux[i] for i in seg_indices]
		coeffs = numpy.polyfit(seg_times, seg_flux, 1)
		costs.append(sum([(coeffs[0] * t  + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)]))
		current = next
	while len(segments) > NUM_SEGS:
		min_index = costs.index(min(costs))
		
		lmerge = None
		rmerge = None
		
		# If we are not at leftmost point, recompute cost of merging with left index
		if min_index != 0: # find lmerge
			new_min = segments[min_index - 1][0]
			new_max = segments[min_index][1]
			seg_indices = range(new_min, new_max + 1) # Include the endpoint
			seg_times = [lc.time[i] for i in seg_indices]
			seg_flux = [lc.flux[i] for i in seg_indices]
			coeffs = numpy.polyfit(seg_times, seg_flux, 1)
			lmerge = sum([(coeffs[0] * t + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)])
		
		# If we are not at rightmost point, recompute cost of merging with right index
		if min_index != len(costs) - 1:
			# Remove first two cost values and replace with one
			new_min = segments[min_index][0]
			new_max = segments[min_index + 2][1] # The index beyond the one with which we merged
			seg_indices = range(new_min, new_max + 1) # Include the endpoint
			seg_times = [lc.time[i] for i in seg_indices]
			seg_flux = [lc.flux[i] for i in seg_indices]
			coeffs = numpy.polyfit(seg_times, seg_flux, 1)
			rmerge = sum([(coeffs[0] * t + coeffs[1] - v) ** 2 for t, v in izip(seg_times, seg_flux)])
		
		# Now remove the old segments, replacing with one new, longer segment
		new_min = segments[min_index][0]
		new_max = segments[min_index + 1][1]
		segments = segments[:min_index] + [[new_min, new_max]] + segments[min_index + 2:] # One beyond the merge point

		# Handle the cost update cases
		if lmerge is None:
			costs = [rmerge] + costs[2:]
		elif rmerge is None:
			costs = costs[:-2] + [lmerge]
		else:
			costs = costs[:min_index - 1] + [lmerge, rmerge] + costs[min_index + 2:]
	for seg in segments:
		min_index = min(seg)
		max_index = max(seg)
		times = []
		flux = []
		for i in xrange(min_index, max_index + 1):
			times.append(lc.time[i])
			flux.append(lc.flux[i])
		plt.plot(times, flux)
	plt.show()
	return segments

def linsegfeatures(lc):
	stddev = numpy.std(lc.flux)
	mean = numpy.mean(lc.flux)
	
	# center the flux
	for index in range(len(lc.flux)):
		lc.flux[index] = (lc.flux[index] - mean) / stddev
	
	segments = linear_segmentation(lc)
	segment_indices = [range(seg[0], seg[1] + 1) for seg in segments]
	segment_times = [[lc.time[i] for i in indices] for indices in segment_indices]
	segment_flux = [[lc.flux[i] for i in indices] for indices in segment_indices]
	coeffs = [numpy.polyfit(ts, fs, 1) for ts, fs in izip(segment_times, segment_flux)]
	line_values = [[coeff[0] * t + coeff[1] for t in s_t] for s_t, coeff in izip(segment_times, coeffs)]
	
	for t, v in izip(segment_times, line_values):
		plt.plot(t, v)
	plt.plot(lc.time, lc.flux)
	plt.show()
	# Complexity distance of the segmentation
	length = 0
	last = None
	for times, vals in izip(segment_times, line_values):
		#print "seg indices:", vals[-1], vals[0], times[-1], times[0]
		#print "seg length:", math.sqrt((vals[-1] - vals[0]) ** 2 + (times[-1] - times[0]) ** 2)
		length += math.sqrt((vals[-1] - vals[0]) ** 2 + (times[-1] - times[0]) ** 2)
		if last is not None:
			#print "jump indices:", last[0], times[0], last[1], vals[1]
			#print "jump length:", math.sqrt((last[0] - times[0]) ** 2 + (last[1] - vals[0]) ** 2)
			length += math.sqrt((last[0] - times[0]) ** 2 + (last[1] - vals[0]) ** 2)
		last = [times[-1], vals[-1]]
	length = length / (1.0 * (lc.time[-1] - lc.time[0]))
	
	# Gradient statistical metrics
	gradient_hist = []
	for seg, coeff in izip(segments, coeffs):
		gradient_hist += [coeff[0] for t in xrange(seg[1] + 1)]
	grad_mean = numpy.mean(gradient_hist)
	grad_median = numpy.median(gradient_hist)
	grad_deviation = numpy.std(gradient_hist)
	grad_kurtosis = scipy.stats.kurtosis(gradient_hist)
	grad_skew = scipy.stats.skew(gradient_hist)
	grad_max = max(gradient_hist)
	grad_min = min(gradient_hist)

	features = [grad_mean, grad_median, grad_deviation, grad_kurtosis,\
		grad_skew, grad_max, grad_min, length]
	return features	
