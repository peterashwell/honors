import os
import sys
import re
import math
import re
# TODO config instead
# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]
RAW_FEAT_DIR = configs["RAW_FEATURE_DIR"]
JOINED_FEAT_DIR = configs["JOINED_FEATURE_DIR"]
NUM_CROSSFOLDS = configs["NUM_CROSSFOLDS"]
RAW_RES_DIR = configs["RAW_RESULT_DIR"]
ACCUM_RES_DIR = configs["ACCUM_RES_DIR"]
CLASSES = configs["CLASSES"]
EXP_CONFIG = configs["EXPERIMENT_CONFIG"]
CLASSIFY_CONFIG = configs["CLASSIFY_CONFIG"]
NUM_CLASSES = len(configs["CLASSES"])
EXP_DIR = sys.argv[1]

true_class_positions = {}
position_class_map = {}
for i, classname in enumerate(sorted(CLASSES)): # IMPORTANT, sorting keeps ordering consistent
	true_class_positions[classname] = i
	position_class_map[i] = classname
if not os.path.isdir(ACCUM_RES_DIR):
	os.mkdir(ACCUM_RES_DIR)
exp_config = open("{0}/{1}".format(EXP_DIR, EXP_CONFIG))
for line in exp_config:
	print "exp config line", line
	line = line.strip().split(',')
	raw_res_dir = "{0}/{1}-{2}".format(RAW_RES_DIR, line[5], line[6])
	print "train:", line[5], "test:", line[6]
	classify_config = open("{0}/{1}".format(EXP_DIR, CLASSIFY_CONFIG))
	for clsf_line in classify_config:
		print "classify config line", clsf_line
		confusion_matrix = [[0 for i in xrange(NUM_CLASSES)] for i in range(NUM_CLASSES)]
		
		clsf_line = clsf_line.strip().split(',')	
		feat_id = clsf_line[0]
		for cf_num in xrange(NUM_CROSSFOLDS):
			result_fname = "{0}/{1}/cf{2}".format(raw_res_dir,feat_id,cf_num)
			print "reading results from", result_fname
			result_file = open(result_fname)	
			these_class_positions = {}
			this_cm = []
			for linenum,cm_line in enumerate(result_file): # care of line variable above
				cm_line = re.split('\s+', cm_line.strip())
				row_class = cm_line[-1]
				these_class_positions[linenum] = row_class # to permute the entries
				this_cm.append([int(o) for o in cm_line[:NUM_CLASSES]]) # build temporary cm
			# now we have built the cm, permute the entries to the correct position 
			for rownum in xrange(NUM_CLASSES):
				permuted_row = true_class_positions[these_class_positions[rownum]]
				for colnum in xrange(NUM_CLASSES):
					permuted_col = true_class_positions[these_class_positions[colnum]]
					confusion_matrix[permuted_row][permuted_col] += this_cm[rownum][colnum]
		# write confusion matrix out and compute some stats about it
		join_cf_dir = "{0}/{1}-{2}".format(ACCUM_RES_DIR, line[5], line[6])
		if not os.path.isdir(join_cf_dir):
			os.mkdir(join_cf_dir)

		cm_out_filename = "{0}/{1}.cm".format(join_cf_dir,feat_id)
		cm_out_file = open(cm_out_filename, 'w')
		cm_rows = [','.join([str(obj) for obj in row]) for row in confusion_matrix]
		for rownum, row in enumerate(cm_rows):
			out_line = position_class_map[rownum] + "," + row
			cm_out_file.write(out_line + '\n')
			print out_line
		#outstr = '\n'.join(','.join([str(obj) for obj in row]) for row in confusion_matrix)
		#cm_out_file.write(outstr)
		#print "cm:", outstr
		cm_out_file.close()
