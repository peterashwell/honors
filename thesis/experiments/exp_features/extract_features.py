import sys
import os
import string
import traceback
import sqlite3
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
	flux = lc.flux[:]
	flux_mean = numpy.mean(flux)
	flux_std = numpy.std(flux)
	centered_flux = [(e - flux_mean) / (1.0 * flux_std) for e in flux]
	lc_centered = LightCurve(lc.time[:], centered_flux)

	return \
		flux_only(lc_centered) + time_flux(lc_centered) + haar_coeffs(lc_with_gaps) + spectral_features(lc_centered)

# takes as input
#		lc_files - light curve filenames to produce an arff from (relative address)
#		cache - the working cache of features mapped from lc filenames
#		cache_keyset - the corresponding keyset
#	produces as output
#		arff_filename - filename for output file
def expdir_to_arff(lc_files, dyncache, dyncache_keyset, exp_dir, arff_fname):
	# Load up the description of each feature (name and #) to use to write the arff
	featdesc_file = open(FEATDESC_FNAME)
	feat_names = []
	feat_counts = {}
	for line in featdesc_file:
		if line[0] == '#':
			continue
		line = line.strip().split('\t')
		feat_names.append(line[0])
		feat_counts[line[0]] = int(line[1])
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
	for feat_name in feat_names:
		if feat_counts[feat_name] == 1: # only 1 feature
			arff_file.write('@ATTRIBUTE {0} NUMERIC\n'.format(feat_name))
		else:
			for i in xrange(feat_counts[feat_name]):
				arff_file.write('@ATTRIBUTE {0}{1} NUMERIC\n'.format(feat_name, str(i)))
	arff_file.write('@ATTRIBUTE class {' + ', '.join(classes) + '}\n\n')
	arff_file.write('@DATA\n')
	
	# extract features if not in cache and append
	# TODO replace cache_file = open(CACHE_FNAME, 'a')
	to_process = len(lc_files)
	lc_file = None
#	try: # to stop corruption of the cache
	increment = int(round((to_process / 10)))
	done = 0
	
	conn = sqlite3.connect('feat_cache.db')
	c = conn.cursor()

	for lc_file in lc_files:
		#print lc_file
		if done % increment == 0 and done != 0:
			print "{0}/{1}".format(done, len(lc_files))
		done += 1

		# look for cache hit
		
		lc_class = lc_file.split('_')[0]
		features = None
		lc_path = '{0}/{1}/{2}'.format(LC_DIR, exp_dir, lc_file)
		#print "extracting features from:", lc_path
		
		# check to see if features are in dynamic cache first
		if lc_path in dyncache_keyset:
			features = dyncache[lc_path]
		else: # do db lookup
			search_cursor = c.execute('''select * from featcache where key=?''', [lc_path])
			search_result = search_cursor.fetchall()
			if len(search_result) == 0: # cache miss, extract features
				print "db miss"
				lc = file_to_lc(lc_path)
				features = lc_to_features(lc)
				c.execute('''insert into featcache values {0}'''.format(tuple([lc_path] + features)))
			else:
				features = search_result[0][1:] # fetch features and remove key
			# either if extracted or fetched from db, add to dynamic cache
			dyncache[lc_path] = features
			dyncache_keyset.add(lc_path)
		# finally, write in the features
		arff_file.write(','.join([str(obj) for obj in features]) + ',' + lc_class + '\n')
	conn.commit()
	conn.close()
	arff_file.close()
	return (dyncache, dyncache_keyset)
#if __name__ == '__main__':
#	if len(sys.argv) <= 1 or len(sys.argv) > 2:
#		print '{0} <dir> produce arff file representing files from <dir> to <dir>.arff'.format(sys.argv[0])
#	else:
#		expdir_to_arff(os.listdir(sys.argv[1]))
