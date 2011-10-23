#Given a time series object, potentially with missing data or sampling, extract features
import scipy
import os
from scipy.stats import *
import lightcurve
import numpy
import math
from lightcurve import LightCurve
import lomb
from operator import itemgetter
from itertools import izip
import matplotlib.pyplot as plt
import utils
import getshoutdir
import distances
NUM_CROSSFOLDS = 10
RAW_FEAT_DIR = "raw_features"

# Find distance from shapelets according to args
# extract for all lightcurves in lc_dir
SHAPELET_TRAIN_DIR = "norm_n0.0_a100_m0_s400"
LC_DIR = "lightcurves" # TODO configure this

def shapelet_features(apply_dir, args):
	# Get the parameters associated with the shapelet arguments given from the expt
	params = getshoutdir.getshfeatdir(args)
	
	# This is the diredtory containing the processed shapelets for the arguments
	shapelet_featureset = params[0]
	shapelet_feature_path = "shapelet_features/{0}".format(shapelet_featureset)
	print "extracting shapelet features using shapelets in:", shapelet_feature_path

	if not os.path.isdir('{0}/{1}'.format("raw_features", shapelet_featureset)):
		os.mkdir('{0}/{1}'.format("raw_features", shapelet_featureset))
	# This is the directory where the resulting features are going
	feature_out_dir = "{0}/{1}/{2}".format(RAW_FEAT_DIR, shapelet_featureset, apply_dir) # zeroth element is directory name
	print "features extracted to:", feature_out_dir
	if os.path.isdir(feature_out_dir):
		print "directory already exists", feature_out_dir
	else:
		print "creating directory:", feature_out_dir
		os.mkdir(feature_out_dir)
	use_dtw = params[1]
	use_md = params[2]
	best_amt = params[3]
	dist_func = None
	if use_md:
		dist_func = distances.mindist
	elif use_dtw:
		dist_func = distances.dtw
	else:
		print "error!, no distance measure being used"
	
	# This is the lightcurve directory to which we apply the shapelets
	apply_dir = LC_DIR + "/" + apply_dir
	for cfnum in xrange(NUM_CROSSFOLDS):
		print "crossfold", cfnum
		#	cf_best = utils.best_shapelets(crossfold + "/cf{0}".format(cfnum))
		test_list = "crossfold/cf{0}/test".format(cfnum)
		for fnum, fname in enumerate(open(test_list)):
			if fnum % 10 == 0:
				print "{0} files processed".format(fnum)
			fname = fname.strip()
			extract_file = apply_dir + "/" + fname
			# Open extraction file to lc
			extract_from = lightcurve.file_to_lc(extract_file)
			features = []
			# Load all the shapelets from shapelet_features/dir/cf(num) and find distances
			shapelet_source_dir = "{0}/cf{1}".format(shapelet_feature_path, cfnum)
			for shapelet_filename in os.listdir(shapelet_source_dir):
				# Get the shapelet cotents and apply the distance measure
				shapelet_as_lc = lightcurve.file_to_lc(shapelet_feature_path + '/cf{0}/'.format(cfnum) + shapelet_filename)
				
				measure_with_flux = shapelet_as_lc.flux
				if len(measure_with_flux) == 0:
					print "missing a shapelet file:", shapelet_feature_path + '/cf{0}/'.format(cfnum) + shapelet_filename        
					continue
				distance = dist_func(extract_from.flux, measure_with_flux)[0]
				features.append(distance)
			# Finally, write out all the features
			feat_outfname = feature_out_dir + "/"  + fname
			feat_outfile = open(feat_outfname, 'w')
			feat_outfile.write(','.join([str(o) for o in features]))
			feat_outfile.close()

def flux_features(lc):
	lc.remove_gaps()
	# Centered and sorted flux to work with
	mean = numpy.mean(lc.flux)
	stddev = numpy.std(lc.flux)
	centered_flux = [(f - mean) / (1.0 * stddev) for f in lc.flux]
	sorted_flux = sorted(centered_flux)

	# Median
	median_pos = len(sorted_flux) / 2
	flux_median = sorted_flux[median_pos]
	
	# Skew
	flux_skew = scipy.stats.skew(centered_flux)

	# Kurtosis
	flux_kurtosis = scipy.stats.kurtosis(centered_flux)

	# Stuff for percentiles
	stddev = scipy.std(centered_flux) # is 1 but let's just do it again anyway
	mean = numpy.mean(centered_flux) # is 0 but we'll be explicit
	
	# Percentiles - one, fraction of data within regular inc * stddev from MEAN
	increments = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75, 1, 1.5, 2, 3]
	flux_pos_percentiles = []
	flux_mean = numpy.mean(centered_flux)
	flux_std = numpy.std(centered_flux)
	inc_upto = 0
	len_flux = len(centered_flux)
	flux_pos = 0
	sorted_pos_flux = sorted(filter(lambda f: f >= 0, centered_flux))
	#print sorted_flux
	for inc in increments:
		f_index = 0
		while f_index < len(sorted_pos_flux) and sorted_pos_flux[f_index] < flux_std * inc:
			f_index += 1
		#print "broke at bandwidth:", flux_std * inc
		if len(sorted_pos_flux) == 0:
			flux_pos_percentiles.append(0)
		else:
			flux_pos_percentiles.append((f_index * 1.0) / len(sorted_pos_flux))
		# Percentiles - one, fraction of data within regular inc * stddev from MEAN

	flux_neg_percentiles = []
	inc_upto = 0
	flux_pos = 0
	sorted_neg_flux = sorted([math.fabs(f) for f in filter(lambda f: f < 0, centered_flux)])
	#print sorted_flux
	for inc in increments:
		f_index = 0
		while f_index < len(sorted_neg_flux) and sorted_neg_flux[f_index] < flux_std * inc:
			f_index += 1
		#print "broke at bandwidth:", flux_std * inc
		if len(sorted_neg_flux) == 0:
			flux_neg_percentiles.append(0)
		else:
			flux_neg_percentiles.append((f_index * 1.0) / len(sorted_neg_flux))
	# Percentiles - two, spread of data within regular inc * stddev from MEDIAN
	#stddev_increments = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75, 1, 1.5, 2, 3]
	#flux_med_percentiles = []
	#for inc in stddev_increments:
	#	in_range = 0
	#	bound = stddev * inc
	#	for f in centered_flux:
	#		if (math.fabs(f) - flux_median) < bound:
	#			in_range += 1
	#	flux_med_percentiles.append((in_range * 1.0) / len(centered_flux))

	# Maximum and minimum
	flux_max = max(centered_flux)
	flux_min = min(centered_flux) 
	#print "flux:", centered_flux
	#print "flux_pos_percentiles:", flux_pos_percentiles
	#print "flux_neg_percentiles:", flux_neg_percentiles
	features = [flux_median, flux_skew, flux_kurtosis] + \
	       [flux_max, flux_min]	+ \
	        flux_pos_percentiles + flux_neg_percentiles #+ flux_med_percentiles
	#print "len flux only:", len(features)
	return features

def spectral_features(lc):
	lc.remove_gaps()
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

def haar_coeffs(lc):
	TOP_COEFFS = 15
	POW_2_USED = 9 # length of 512 for all lcs
	#next_pow_2 = int(math.ceil(math.log(len(lc.time), 2)))
	# arithmetical error...
	#if 2 ** next_pow_2 < len(lc.time):
	#	next_pow_2 += 1
	filled_lc = LightCurve(lc.time[:], lc.flux[:])
	
	# fill out lc with blanks '-'
	remaining = 2 ** POW_2_USED - len(filled_lc.time)
	filled_lc.time += range(int(lc.time[-1]) + 1, int(lc.time[-1]) + remaining + 1)
	filled_lc.flux += ['-'] * remaining
	
	transform = utils.haar_transform(filled_lc.flux)
	# normalise the transformed haar spectra, and fill in missing data with 0s
	norm_transform = []
	# replace missing data with 0 coefficient
	for item in transform:
		if item == '-':
			norm_transform.append(0.0)
		else:
			norm_transform.append(item)
	norm_transform = norm_transform[:TOP_COEFFS] # take TOP_COEFF number of coeffs
	#if len(norm_transform) < TOP_COEFFS:
	#	norm_transform += [0.0] * (TOP_COEFFS - len(norm_transform))
	return norm_transform

def grad_features(lc):
	# Center the flux
	lc.remove_gaps()
	stddev = numpy.std(lc.flux)
	mean = numpy.mean(lc.flux)
	for index in range(len(lc.flux)):
		lc.flux[index] = (lc.flux[index] - mean) / stddev
	
	segments = utils.linear_segmentation(lc)
	segment_indices = [range(seg[0], seg[1] + 1) for seg in segments]
	segment_times = [[lc.time[i] for i in indices] for indices in segment_indices]
	segment_flux = [[lc.flux[i] for i in indices] for indices in segment_indices]
	coeffs = [numpy.polyfit(ts, fs, 1) for ts, fs in izip(segment_times, segment_flux)]
	line_values = [[coeff[0] * t + coeff[1] for t in s_t] for s_t, coeff in izip(segment_times, coeffs)]
	
	# Complexity distance
	length = 0
	last = None
	for times, vals in izip(segment_times, line_values):
		length += math.sqrt((vals[-1] - vals[0]) ** 2 + (times[-1] - times[0]) ** 2)
		if last is not None:
			length += math.sqrt((last[0] - times[0]) ** 2 + (last[1] - vals[0]) ** 2)
		last = [times[-1], vals[-1]]
	complexity_dist = length / (1.0 * (lc.time[-1] - lc.time[0]))
	
	# Gradient statistical features
	gradients = [] # Build histogram of gradient masses
	for seg, coeff in izip(segments, coeffs):
		gradients += [coeff[0] for t in xrange(seg[0], seg[1] + 1)]
	grad_mean = numpy.mean(gradients)
	grad_med = numpy.median(gradients)
	grad_stddev = numpy.std(gradients)
	grad_kurtosis = scipy.stats.kurtosis(gradients)
	grad_skew = scipy.stats.skew(gradients)
	grad_max = max(gradients)
	grad_min = min(gradients)

	# Gradient percentiles (from histogram) (MEDIAN and MEAN)
	increments = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.75, 1, 1.5, 2, 3]
	grad_pos_percentiles = []
#	print gradients
	sorted_pos_gradients = sorted(filter(lambda g: g >= 0, gradients))
	for inc in increments:
		g_index = 0
		while g_index < len(sorted_pos_gradients) and sorted_pos_gradients[g_index] < grad_stddev * inc:
			g_index += 1
		len_gradients = len(sorted_pos_gradients)
		if len_gradients == 0:
			grad_pos_percentiles.append(0)
		else:
			grad_pos_percentiles.append((g_index * 1.0) / len_gradients)
	
	grad_neg_percentiles = []
	sorted_neg_gradients = sorted([math.fabs(f) for f in filter(lambda g: g < 0, gradients)])
	#nprint sorted_neg_gradients
	#print len(sorted_neg_gradients)
	for inc in increments:
		g_index = 0
		while g_index < len(sorted_neg_gradients) and sorted_neg_gradients[g_index] < grad_stddev * inc:
			g_index += 1
		len_gradients = len(sorted_neg_gradients)
		if len_gradients == 0:
			grad_neg_percentiles.append(0)
		else:
			grad_neg_percentiles.append((g_index * 1.0) / len_gradients)
	
	#	mean_within_buf = 0
	#	med_within_buf = 0
	#	buffer = grad_stddev * tol
	#	for g in gradients:
	#		if math.fabs(g - grad_mean) < buffer:
	#			mean_within_buf += 1
	#		if math.fabs(g - grad_med) < buffer:
	#			med_within_buf += 1
	#	grad_mean_percentiles.append(mean_within_buf / (1.0 * len(gradients)))
	#	grad_med_percentiles.append(med_within_buf / (1.0 * len(gradients)))
	#print "gradients:", gradients, len(gradients)
	#print "grad_pos_percentiles:", grad_pos_percentiles
	#print "grad_neg_percentiles:", grad_neg_percentiles
	features = [grad_mean, grad_stddev, grad_med, grad_skew, \
	            grad_kurtosis, grad_max, grad_min, complexity_dist] \
	            + grad_pos_percentiles + grad_neg_percentiles
	#print "len time flux:", len(features)
	return features
