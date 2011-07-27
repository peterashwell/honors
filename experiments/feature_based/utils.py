import random
from features import *
import os
from lightcurve import LightCurve
from do import wekafy_lightcurves

LC_DIRECTORY = "../lightcurves"
# Produce lc object from file
def file_to_lc(filename):
	#print "creating lc from:", filename
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
	return LightCurve(time, flux)

# yields crossfolds of 90/10 training/test split perfect/distorted data filenames
# corresponding to weka .arff file formats as training/test pairs
# directories are from ../lightcurves
def distorted_lc_crossfold(train_dir, test_dir, arffdir):
	experiment_name = test_dir
	NUM_FOLDS = 10
	crossfold_files = [] # train/test filenames (returned)

	# Collect all lc files according to class
	files_by_class = {}
	for file in os.listdir(LC_DIRECTORY +'/' + train_dir):
		lc_class = file.strip().split('_')[0]
		if lc_class in files_by_class.keys():
			files_by_class[lc_class].append(file)
		else:
			new_list = [file]
			files_by_class[lc_class] = new_list
	
	# For each crossfold, check the file exists in the test directory (distorted)
	# If it doesn't exist, raise an error, otherwise, build weka files
	fold_residues = {}
	for class_key in files_by_class.keys():
		fold_residues[class_key] = len(files_by_class[class_key]) % NUM_FOLDS
	
	# build lists of lc filenames to be used in training and testing (each crossfold)
	train_folds = [[] for i in xrange(NUM_FOLDS)]
	test_folds = [[] for i in xrange(NUM_FOLDS)]
	cache = {} # cache of already computed lightcurve properties
	fold_start = 0
	#print "class keys:", files_by_class.keys()
	for ck in files_by_class.keys():
		fold_start = 0
		fold_length = len(files_by_class[ck]) / NUM_FOLDS # integer divide, see above
		for fold_num in xrange(NUM_FOLDS):
			fold_end = fold_start + fold_length
			if fold_residues[ck] > 0:
				fold_residues[ck] -= 1
				fold_end += 1
			#print "fold start:", fold_start
			#print "fold end:", fold_end
			#print "len train addition:", len(files_by_class[ck][:fold_start] + files_by_class[ck][fold_end:])
			#print "len test addition:", len(files_by_class[ck][fold_start:fold_end])
			train_folds[fold_num] +=  files_by_class[ck][:fold_start] + files_by_class[ck][fold_end:]
			test_folds[fold_num] += files_by_class[ck][fold_start:fold_end]
			fold_start = fold_end
	# Add all the light curves 
	for fold_num in xrange(NUM_FOLDS):
		print "producing crossfold", fold_num
		train_filename = arffdir + '/' + experiment_name + "_train{0}.arff".format(fold_num)
		test_filename = arffdir + '/' + experiment_name + "_test{0}.arff".format(fold_num)
		#print len(train_folds[fold_num]), len(test_folds[fold_num])
		cache = wekafy_lightcurves(train_dir, train_folds[fold_num], train_filename, cache)
		cache = wekafy_lightcurves(test_dir, test_folds[fold_num], test_filename, cache)
		crossfold_files.append((train_filename, test_filename))
	#print crossfold_files
	return crossfold_files # classify on these
