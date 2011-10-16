import os
# Takes an experiment directory as input and processes all its result confusion matrix files
# Creates files <featname>.summary and <featname>.details in the results/<train><test> directory

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
EXP_DIR = sys.argv[1]

exp_config = open("{0}/{1}".format(EXP_DIR, EXP_CONFIG))
for line in exp_config:
	line = line.strip().split(',')
	result_dir = "{0}/{1}-{2}".format(ACCUM_RES_DIR, line[5], line[6])
	classify_config = open("{0}/{1}".format(EXP_DIR, CLASSIFY_CONFIG))
	for clsf_line in classify_config:
		clsf_line = clsf_line.strip().split(',')
		featset = clsf_line[0]
		# First read in the confusion matrix
		#class_position = {}
		#position_class = {}
		confusion_matrix = []
		cm_filename = open("{0}/{1}.cm".format(result_dir,featset))
		for linenum, cm_line in enumerate(cm_filename):
			confusion_matrix.append(cm_line.split(','))
		cm_filename.close()
		# Start computing metrics
		class_results, total_results = utils.process_cm(confusion_matrix)
		summary_file = open("{0}/{1}.summary".format(result_dir,featset), 'w')
		detail_file = open("{0}/{1}.details".format(result_dir,featset), 'w')
		summary_file.write('\n'.join([str(o) for o in total_results]))
		print total_results
		detail_file.write('\n'.join([','.join([str(o) for o in row]) for row in class_results]))
		summary_file.close()
		detail_file.close()
