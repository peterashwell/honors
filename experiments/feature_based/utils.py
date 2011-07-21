import random
from features import *
import os

def file_to_lc(filename):
	print "reading:", filename
	lc_file = open(filename)
	time = []
	flux = []
	for line in lc_file:
		line = line.strip().split(',')
		time.append(float(line[0]))
		if line[1] == '-':
			flux.append('-')
		else:
			flux.append(float(line[1]))
	return [time, flux]

def chop_gaps(lc):
	new_lc = [[],[]]
	for index, t in enumerate(lc[0]):
		if lc[1][index] != '-':
			new_lc[0].append(lc[0][index])
			new_lc[1].append(lc[1][index])
	return new_lc

feature_structure = [\
("stddev", 1),\
("beyond1std", 1),\
("skew", 1),\
("kurtosis", 1),\
("flux_percentiles", 5),\
("amplitude_spread", 1),\
("median_deviation", 1),\
("median_buffer", 1),\
("max_slope", 1),\
("haar_transform", 8),\
("spectral_features", 4),\
("slope_pair_trends", 1),\
]

def allfeatures(lc):
	unchopped = [lc[0][:], lc[1][:]]
	lc = chop_gaps(lc)
	return stddev(lc) + beyond1std(lc) + skew(lc) + \
		kurtosis(lc) + flux_percentiles(lc) + amplitude_spread(lc) + \
		median_deviation(lc) + median_buffer(lc) + \
		max_slope(lc) + haar_transform(unchopped) + spectral_features(lc) + slope_pair_trends(lc)

# produce weka file representing the light curve's features
def wekafy_lightcurves(dir):
	weka_filename = dir + ".arff"
	if weka_filename in os.listdir(dir):
		print "arff already exists"
		return False # abandon building arff
	# otherwise, build it
	weka_file = open(weka_filename, 'w')
	weka_file.write("% Light curve classification features\n\n")
	weka_file.write("@RELATION light_curves\n\n")
	for feature_info in feature_structure:
		if feature_info[1] == 1: # only 1 feature
			weka_file.write("@ATTRIBUTE {0} NUMERIC\n".format(feature_info[0]))
		else:
			for i in xrange(feature_info[1]):
				weka_file.write("@ATTRIBUTE {0}{1} NUMERIC\n".format(feature_info[0], str(i)))
	weka_file.write("@ATTRIBUTE class {SNe, Noise, Flare, Novae, IDV, ESE}\n\n")
	weka_file.write("@DATA\n")
	for lc_filename in os.listdir(dir):
		print "reading:", lc_filename
		lc = file_to_lc(dir + '/' + lc_filename)
		lc_class = lc_filename.split('_')[0]
		features = allfeatures(lc)
		if len(features) != 26:
			print "asdf", len(features)
		weka_file.write(','.join([str(obj) for obj in features]) + ',' + lc_class + '\n')
	weka_file.close()
