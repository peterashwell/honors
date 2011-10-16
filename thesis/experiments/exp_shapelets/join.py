# Produces an arff file from an exp.config and the raw_features directory

import sys
import os
import lightcurve
from features import *

# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]
RAW_FEAT_DIR = configs["RAW_FEATURE_DIR"]
ARFF_DIR = configs["JOINED_FEATURE_DIR"]
NUM_CROSSFOLDS = configs["NUM_CROSSFOLDS"]
FEAT_CONFIG = configs["CLASSIFY_CONFIG"]
EXP_CONFIG = configs["EXPERIMENT_CONFIG"]
CLASSES = configs["CLASSES"]
exp_dir = sys.argv[1] # get directory of experiment to process

# Use the exp.config at the sys.argv[1] location to decide what to join
feature_config = open("{0}/{1}".format(exp_dir, FEAT_CONFIG))
join_features = []
for line in feature_config:
	line = line.strip()
	join_features.append(line)
exp_config = open("{0}/{1}".format(exp_dir, EXP_CONFIG))

# Create raw feature dir if necessary
if not os.path.isdir(ARFF_DIR):
	os.mkdir(ARFF_DIR)

# Start joining the features as per instruction, writing to an arff file
for line in exp_config:
	line = line.strip().split(',')
	exp_id = line[0]
	train = line[5]
	test = line[6]
	
	exp_arff_dir = "{0}/{1}-{2}".format(ARFF_DIR, train, test)
	if os.path.isdir(exp_arff_dir):
		print "arff directory", exp_arff_dir, "already exists. skipping..."
		continue
	os.mkdir(exp_arff_dir)

	for feat_join in join_features:
		feat_join = feat_join.strip().split(',')
		join_id = feat_join[0]
		join_name = feat_join[1]
		args = feat_join[2:]
		print "join id:", join_id
		print "args:", args
		# Find feature files in crossfold and copy over
		for cfnum in xrange(NUM_CROSSFOLDS):
			this_arff_cf_dir = "{0}/cf{1}".format(exp_arff_dir, cfnum)
			if not os.path.isdir(this_arff_cf_dir):
				os.mkdir(this_arff_cf_dir)
			for train_test in ["train", "test"]:
				join_cf_dir = "{0}/{1}".format(this_arff_cf_dir, join_id)
				if not os.path.isdir(join_cf_dir):
					os.mkdir(join_cf_dir)
				print "joining feature set", join_cf_dir
				arff_fname = join_cf_dir + "/" + train_test + ".arff"
				print "arff file:", arff_fname
				lc_cf_filename = "{0}/cf{1}/{2}".format(CF_DIR, cfnum, train_test)
				print "reading lcs from:", lc_cf_filename
				arff_outfile = open(arff_fname, 'w')
				feature_lengths = {} # figure out feature lengths on the go
				feature_block = [] # block of lines to write into @data section
				for fname in open(lc_cf_filename):
					joined_features = []
					for featname in args:
						# TODO write to header here
						feature_file = "{0}/{1}".format(RAW_FEAT_DIR, featname)
						if train_test == "train":
							feature_file += "/" + train
						elif train_test == "test":
							feature_file += "/" + test
						feature_file += "/" + fname.strip()
						print "reading features from", feature_file
						features = open(feature_file).read().strip().split(',')[1:] # omit filename
						joined_features += features
						if featname not in feature_lengths.keys():
							feature_lengths[featname] = len(features)
						elif feature_lengths[featname] != len(features):
							print "fatal error: inconsistent feature lengths. exiting..."
							exit(0)
					print "adding filename:", [fname.split('/')[-1].split('_')[0]] # Get the class
					joined_features += [fname.split('/')[-1].split('_')[0]] # Get the class
					feature_block.append(joined_features) # add onto the block
					#arff_outfile.write(','.join(joined_features) + '\n')
				# Start writing out the features and header
				arff_outfile.write("% Features for transient classification, experiment: {0}\n".format(join_name))
				arff_outfile.write("@RELATION {0}\n".format(join_id))
				for featname in feature_lengths.keys():
					if feature_lengths[featname] == 1:
						arff_outfile.write('@ATTRIBUTE {0} NUMERIC\n'.format(featname))
					else:
						for featnum in xrange(feature_lengths[featname]):
							arff_outfile.write('@ATTRIBUTE {0}{1} NUMERIC\n'.format(featname, featnum))
				arff_outfile.write('@ATTRIBUTE class {' + ','.join(CLASSES) + '}\n\n')
				arff_outfile.write('@DATA\n')
				joined_rows = [','.join([str(o) for o in row]) for row in feature_block]
				joined_block = '\n'.join(joined_rows)
				arff_outfile.write(joined_block)
				arff_outfile.close()
