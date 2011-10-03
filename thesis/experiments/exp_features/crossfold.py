import os
import sys
from extract_features import expdir_to_arff
# crossfold producing code
# takes as input
#		train_dir - the directory of the training data
#		test_dir - the directory containing the test data
#		output_dir - the desired directory to write the arff files
# and places two arff files named <train_dir>.arff <test_dir>.arff in <output_dir>

NUM_FOLDS = 10
LC_DIR = '../lightcurves'
CACHE_FNAME = 'features.cache'
ARFF_DIR = 'arff'

def dir_crossfold(train_dir, test_dir, out_dir):
	# group light curves by class
	lc_by_class = {}
	for file in os.listdir('{0}/{1}'.format(LC_DIR, train_dir)):
		lc_class = file.strip().split('_')[0]
		if lc_class in lc_by_class.keys():
			lc_by_class[lc_class].append(file)
		else:
			new_list = [file]
			lc_by_class[lc_class] = new_list
	#print lc_by_class
	
	# initialise cache
	dyncache = {}
	dyncache_keyset = set()
	#print "loading cache..."
	# load cache from CACHE_FNAME
	#cache = {}
	#cachefile = open(CACHE_FNAME)
	#for line in cachefile:
	#	line = line.strip().split(',')
	#	lc_filename = line[0] #'{0}/{1}/{2}'.format(LC_DIR, exp_dir, line[0])
	#	if lc_filename not in cache.keys():
	#		features = [float(obj) for obj in line[1:]]
	#		cache[lc_filename] = features
	#cache_keyset = set(cache.keys())
	#cachefile.close()
	
	# get the number of residue light curves for each class
	residues_by_class = {}
	for c in lc_by_class.keys():
		residues_by_class[c] = len(lc_by_class[c]) % NUM_FOLDS
	#print residues_by_class

	# lists containing train and test lc files for each crossfold
	train_folds = [[] for i in xrange(NUM_FOLDS)]
	test_folds = [[] for i in xrange(NUM_FOLDS)]

	print "creating crossfold arff files..."
	# for each class, add the light curve files to each crossfold
	for c in lc_by_class.keys():
		fold_start = 0
		fold_length = len(lc_by_class[c]) / NUM_FOLDS
		for fold_num in xrange(NUM_FOLDS):
			fold_end = fold_start + fold_length
			if residues_by_class[c] > 0:
				residues_by_class[c] -= 1
				fold_end += 1
			train_folds[fold_num] += \
				lc_by_class[c][:fold_start] + lc_by_class[c][fold_end:]
			test_folds[fold_num] += \
				lc_by_class[c][fold_start:fold_end]
			fold_start = fold_end

	crossfold_files = []
	
	# produce the arff files for the light curve files in the crossfolds
	for fold_num in xrange(NUM_FOLDS):
		print "file {0} of {1}".format(fold_num + 1, NUM_FOLDS)
		train_filename = '{0}/{1}/train{2}.arff'.format(out_dir, test_dir, fold_num)
		test_filename = '{0}/{1}/test{2}.arff'.format(out_dir, test_dir, fold_num)
		dyncache, dyncache_keyset = expdir_to_arff(train_folds[fold_num], dyncache, dyncache_keyset, train_dir, train_filename)
		dyncache, dyncache_keyset = expdir_to_arff(test_folds[fold_num], dyncache, dyncache_keyset, test_dir, test_filename)
		crossfold_files.append((train_filename, test_filename))
	return crossfold_files

if __name__ == '__main__':
	if (sys.argv) < 1:
		print '<train> <test> <out> produce arff files for <train>/<test> 90/10 crossfolds to <out> dir'
	dir_crossfold(sys.argv[1], sys.argv[2], sys.argv[3])	
