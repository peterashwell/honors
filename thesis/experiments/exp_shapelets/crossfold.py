# Separate files as evenly as possible into 90/10 partitions from train/test sets
# 90/10 is for 10-fold, determined by NUM_FOLDS in config

import sys
import os
import shutil

# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR= configs["LIGHTCURVE_DIR"]
NUM_FOLDS = configs["NUM_CROSSFOLDS"]
RAW_DATA_DIR = configs["RAW_DATA_DIR"]
#TEST_DIR = sys.argv[2]
#OUT_DIR = "{0}/{1}-{2}".format(CF_DIR, RAW_DATA_DIR, TEST_DIR)

#print "train: {0} test: {1}, out: {2}".format(RAW_DATA_DIR, TEST_DIR, OUT_DIR)
if not os.path.isdir(CF_DIR):
	print "creating crossfold directory"
	os.mkdir(CF_DIR)
else:
	print "crossfold directory exists, exiting..."
	exit(0)
# 1) Collect lightcurves by class, assumes that TRAIN and TEST are symmetric (if not the same)
lc_by_class = {}
for filename in os.listdir("{0}/{1}".format(LC_DIR, RAW_DATA_DIR)):
	lc_class = filename.strip().split('_')[0]
	if lc_class in lc_by_class.keys():
		lc_by_class[lc_class].append(filename)
	else:
		new_list = [filename]
		lc_by_class[lc_class] = new_list
# get the number of residue light curves for each class
residues_by_class = {}
for c in lc_by_class.keys():
	residues_by_class[c] = len(lc_by_class[c]) % NUM_FOLDS

# lists containing train and test lc filenames for each crossfold
train_folds = [[] for i in xrange(NUM_FOLDS)]
test_folds = [[] for i in xrange(NUM_FOLDS)]

# Distribute filenames to crossfolds
for c in lc_by_class.keys():
	lc_by_class[c].sort() # VERY IMPORTANT FOR MAINTAINING CONSISTENCY ACROSS CROSSFOLDS
	fold_start = 0
	fold_length = len(lc_by_class[c]) / NUM_FOLDS
	for fold_num in xrange(NUM_FOLDS):
		fold_end = fold_start + fold_length
		if residues_by_class[c] > 0:
			residues_by_class[c] -= 1
			fold_end += 1
		training_part = lc_by_class[c][fold_start:fold_end]
		train_folds[fold_num] += training_part
		
		testing_part = lc_by_class[c][:fold_start] + lc_by_class[c][fold_end:]
		test_folds[fold_num] += testing_part

		# Now increment the fold position
		fold_start = fold_end

# Copy files from train and test directories to appropriate directory in crossfold
for fold_num in xrange(NUM_FOLDS):
	cf_fold_dir = "{0}/cf{1}".format(CF_DIR, fold_num)
	os.mkdir(cf_fold_dir)
	fold_test_file = open("{0}/train".format(cf_fold_dir), 'w')
	fold_train_file = open("{0}/test".format(cf_fold_dir), 'w')

	print "creating directory:", cf_fold_dir
	#print "creating directo`ry:", fold_test_dir
	#os.mkdir(fold_test_dir)
	#print "creating directory:", fold_train_dir
	#os.mkdir(fold_train_dir)
	
	#print "moving", len(train_folds[fold_num]), "lightcurves"
	#print "moving", len(test_folds[fold_num]), "lightcurves"

	# VERY IMPORTANT FOR CORRECT RESULTS
	train_folds[fold_num].sort()
	test_folds[fold_num].sort()
	fold_train_file.write('\n'.join(train_folds[fold_num]))
	fold_test_file.write('\n'.join(test_folds[fold_num]))	
	
	# Old way
	#for fname in test_folds[fold_num]:
	#	print "copying from {0}/{1}/{2}".format(LC_DIR, TEST_DIR, fname), "to {0}/test/".format(cf_fold_dir)
	#		shutil.copyfile("{0}/{1}/{2}".format(LC_DIR, TEST_DIR, fname), "{0}/test/{1}".format(cf_fold_dir,fname))
