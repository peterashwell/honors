import sys
import os
import string
import traceback
from lightcurve import LightCurve
from lightcurve import file_to_lc
from features import *

ARFF_DIR = 'arff'
LC_DIR = 'lightcurves'
CACHE_FNAME = 'features.cache'
FEATDESC_FNAME = 'features.desc'
CLASS_FNAME = 'classes.desc'

# probably doesn't need to be in a method
def lc_to_features(lc):
	lc_with_gaps = lc.copy() # see ../lightcurve.py
	lc.remove_gaps() # see ../lightcurve.py
	return \
		stddev(lc) + \
		beyond1std(lc) + \
		skew(lc) + \
		kurtosis(lc) + \
		flux_percentiles(lc) + \
		amplitude_spread(lc) + \
		median_deviation(lc) + \
		median_buffer(lc) + \
		max_slope(lc) + \
		slope_pair_trends(lc) + \
		haar_transform(lc_with_gaps) + \
		spectral_features(lc)

# takes as input
#		lc_files - light curve filenames to produce an arff from (relative address)
#		cache - the working cache of features mapped from lc filenames
#		cache_keyset - the corresponding keyset
#	produces as output
#		arff_filename - filename for output file
def expdir_to_arff(lc_files, exp_dir, arff_fname, cache, cache_keyset):
	# Load up the description of each feature (name and #) to use to write the arff
	featdesc_file = open(FEATDESC_FNAME)
	feat_struct = {}
	for line in featdesc_file:
		if line[0] == '#':
			continue
		line = line.strip().split('\t')
		feat_struct[line[0]] = int(line[1])
	
	# and the classes
	class_file = open(CLASS_FNAME)
	classes = []
	for line in class_file:
		line = line.strip()
		classes.append(line)
		
	# produce the filename and its header
	arff_file = open(arff_fname, 'w')
	arff_file.write("% Light curve classification features\n\n")
	arff_file.write("@RELATION {0}\n\n".format(exp_dir))
	for feat_name in feat_struct.keys():
		if feat_struct[feat_name] == 1: # only 1 feature
			arff_file.write('@ATTRIBUTE {0} NUMERIC\n'.format(feat_name))
		else:
			for i in xrange(feat_struct[feat_name]):
				arff_file.write('@ATTRIBUTE {0}{1} NUMERIC\n'.format(feat_name, str(i)))
	arff_file.write('@ATTRIBUTE class {' + ', '.join(classes) + '}\n\n')
	arff_file.write('@DATA\n')
	
	# extract features if not in cache and append
	cache_file = open(CACHE_FNAME, 'a')
	to_process = len(lc_files)
	lc_file = None
#	try: # to stop corruption of the cache
	increment = int(round((to_process / 5)))
	done = 0
	for lc_file in lc_files:
		#print lc_file
		#if done % increment == 0 and done != 0:
		#	print "{0}/{1}".format(done, len(lc_files))
		done += 1

		# look for cache hit
		lc_class = lc_file.split('_')[0]
		features = None
		lc_path = '{0}/{1}/{2}'.format(LC_DIR, exp_dir, lc_file)
		if lc_path in cache_keyset: #cache hit
			features = cache[lc_path]
		else: # update the cache
			lc = file_to_lc(lc_path)
			features = lc_to_features(lc)
			cache[lc_path] = features
			cache_file.write('{0},{1}\n'.format(lc_path, ','.join([str(obj) for obj in features])))
			cache_keyset.add(lc_path)
		# write the features to the arff
		arff_file.write(','.join([str(obj) for obj in features]) + ',' + lc_class + '\n')
#	except Exception, e:
#		print 'error occurred while processing', lc_file, e
#		traceback.print_stack()
#		cache_file.close() # prevent corruption to cache
	# done	
	cache_file.close()
	arff_file.close()
	return (cache, cache_keyset)

#if __name__ == '__main__':
#	if len(sys.argv) <= 1 or len(sys.argv) > 2:
#		print '{0} <dir> produce arff file representing files from <dir> to <dir>.arff'.format(sys.argv[0])
#	else:
#		expdir_to_arff(os.listdir(sys.argv[1]))
