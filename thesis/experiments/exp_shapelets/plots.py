# Given an experiment directory, produces the plots and latex required to visualize the results

import os
import sys
import re
import math
import re
import utils

# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]
RAW_FEAT_DIR = configs["RAW_FEATURE_DIR"]
JOINED_FEAT_DIR = configs["JOINED_FEATURE_DIR"]
NUM_CROSSFOLDS = configs["NUM_CROSSFOLDS"]
ACCUM_RES_DIR = configs["ACCUM_RES_DIR"]
CLASSES = configs["CLASSES"]
EXP_CONFIG = configs["EXPERIMENT_CONFIG"]
CLASSIFY_CONFIG = configs["CLASSIFY_CONFIG"]
EXP_DETAILS = configs["EXPERIMENT_DETAILS"]
EXP_DIR = sys.argv[1]

# Collect all the required data then output the pieces and produce figures
# Big plot needs
#		- Map of featset -> class -> param -> fscore
#		- List of params would be nice
#		- Param name
#		- List of classes
#		- List of featuresets
#		- Feature names
#		- Experiment description
#	Confusion matrices need
#		- Confusion matrices by param value
#		- Experiment desription
#		- Param values
#		- Param name
#	Samples need
#		- Param values
#		- Param name
#		- Test directory location
#		- List of classes to make things easy
# These need to be produced for each experiment, so the functions are called
# at the bottom of the first while loop. See utils.py for the functions
exp_config = open("{0}/{1}".format(EXP_DIR, EXP_CONFIG))
exp_details = open("{0}/{1}".format(EXP_DIR, EXP_DETAILS)).read().strip().split('\n')
PARAM_NAME = exp_details[0]
EXP_DESC = exp_details[1]

PARAMS = []
PARAM_FS_CONFMAT = {}

# Read experiment configs, build at both levels
FSCORES = {}
ERRORS = {}
FEATSETS = set() # feature sets seen
FEATSET_DESC = {} # description of features
TEST_DIRS = []
fs_param_cm = {}

for line in exp_config:
	print line
	line = line.strip().split(',')
	param = line[2]
	PARAMS.append(param) # param list
	TEST_DIRS.append(line[6]) # test dir
	result_dir = "{0}/{1}-{2}".format(ACCUM_RES_DIR, line[5], line[6])
	# Start accumulating data to put into the functions
	classify_config = open("{0}/{1}".format(EXP_DIR, CLASSIFY_CONFIG))
	for clsf_line in classify_config:
		print "ident0", clsf_line
		clsf_line = clsf_line.strip().split(',')
		featset = clsf_line[0]
		FEATSETS.add(clsf_line[0])
		FEATSET_DESC[featset] = clsf_line[1]
		# First read in the confusion matrix
		#class_position = {}
		#position_class = {}
		confusion_matrix = []
		cm_filename = open("{0}/{1}.cm".format(result_dir,featset))
		for linenum, cm_line in enumerate(cm_filename):
			confusion_matrix.append(cm_line.split(','))
		cm_filename.close()
		if param not in PARAM_FS_CONFMAT.keys():
			new_dict = {featset : confusion_matrix}
			PARAM_FS_CONFMAT[param] = new_dict
		else:
			PARAM_FS_CONFMAT[param][featset] = confusion_matrix
		# Get the results
		class_results, total_results = utils.process_cm(confusion_matrix)
		error = float(open("{0}/{1}.error".format(result_dir, featset)).read().strip())
		#params_resultsets[param][featset] = {}
		#for resultset in class_results:
		#	params_resultsets[param][featset][class_results[0]] = class_results[1:]
		if featset not in FSCORES.keys():
			FSCORES[featset] = [total_results[-1]]
		else:
			FSCORES[featset].append(total_results[-1]) # gets FSCOREZ
		if featset not in ERRORS.keys():
			ERRORS[featset] = [error]
		else:
			ERRORS[featset].append(error)
print FSCORES # what we need for it	
print PARAMS
print FEATSETS
print FEATSET_DESC
print "ERRORS:", ERRORS
result_tex = ""
result_tex += utils.primary_plot(PARAMS, FSCORES, ERRORS, list(FEATSETS), FEATSET_DESC, EXP_DESC, PARAM_NAME, 0)
result_file = open('{0}/texplot.tex'.format(EXP_DIR), 'w')
result_file.write(result_tex)
result_file.close()

result_tex = ""
# read confmat config
for line in open('{0}/cmlayout.config'.format(EXP_DIR)):
	featureset = line.strip().split(',')
	result_tex += utils.confmat_page(PARAMS, featureset, FEATSET_DESC, PARAM_FS_CONFMAT, PARAM_NAME, EXP_DESC)
result_file = open('{0}/texcms.tex'.format(EXP_DIR), 'w')
result_file.write(result_tex)
result_file.close()
print TEST_DIRS
print EXP_DESC
sample_tex = utils.produce_expsamp(TEST_DIRS, PARAMS, PARAM_NAME, EXP_DESC)
result_file = open('{0}/texsamples.tex'.format(EXP_DIR), 'w')
result_file.write(sample_tex)
result_file.close()
