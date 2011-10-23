# Script to extract features
#		1) Store in corresponding directory to crossfold split (either hybrid or symmetric)
#		2) Keep organised by feature name as well

import sys
import os
import lightcurve
from features import *
import getshoutdir
# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]
RAW_FEAT_DIR = configs["RAW_FEATURE_DIR"]
JOINED_FEAT_DIR = configs["JOINED_FEATURE_DIR"]
NUM_CROSSFOLDS = configs["NUM_CROSSFOLDS"]
# Read features.config file in experiment directory and extract features
# Features stored as:
#	features/
#		<featurename>/ -- Might include some config info (eg length)
#			<sourcedirectory>/ -- May be a complex term for shapelets
#				train0
#				test0
#				...

FEATURE_CONFIG_FILE = "features.config"
EXP_CONFIG_FILE = "exp.config"
EXP_DIR = sys.argv[1]
print "experiment directory:", EXP_DIR

# Read "compute" section of the experiment and extract all
feature_config = open("{0}/{1}".format(EXP_DIR, FEATURE_CONFIG_FILE))
comp_features = {}
for line in feature_config:
	line = line.strip().split(',')
	comp_features[line[0]] = line[1:]
print comp_features
# Read experiment config, and extract features for each
exp_config = open("{0}/{1}".format(EXP_DIR, EXP_CONFIG_FILE))

if not os.path.isdir(RAW_FEAT_DIR):
	os.mkdir(RAW_FEAT_DIR)

for line in exp_config:
	line = line.strip().split(',')
	exp_id = line[0]
	train = line[5]
	test = line[6]
	# Take each file from crossfold, extract features and place in raw features
	for feat_id in comp_features.keys():
		# check if feature has already been computed
		exp_feat_dir = "{0}/{1}".format(RAW_FEAT_DIR, feat_id)
		if not os.path.isdir(exp_feat_dir):
			os.mkdir(exp_feat_dir)
		# Extract features from every light curve in training directory
		print "extracting features for", exp_feat_dir
		for train_test in [train, test]: # just for convenience
			# Extract shapelets if necessary (external step to other feature extraction)
			if "shapelet" in feat_id:
				print "extracting shapelet features for directory:", train_test
				shapelet_features(train_test, comp_features[feat_id][0]) # extract all shapelets for train_test with args
				continue # do not proceed (what would we do anyway?)
			outdir = "{0}/{1}".format(exp_feat_dir, train_test)
			if os.path.isdir(outdir):
				print "features already extracted to", outdir, "skipping"
				continue
			os.mkdir(outdir)
			
			lcs_to_extract = os.listdir("{0}/{1}".format(LC_DIR, train_test))
			for fname in lcs_to_extract:
				outfile = open("{0}/{1}".format(outdir,fname), 'w')
				if fname == ".DS_Store": # skip this stupid shit
					continue
				data_fname = "{0}/{1}/{2}".format(LC_DIR, train_test, fname)
				lc = lightcurve.file_to_lc(data_fname)
				features = [data_fname] + apply(eval(feat_id),[lc])
				outfile.write(','.join([str(o) for o in features]) + '\n')
			outfile.close()
