import sys
import os
import re
import math

TEMPRES_DIR = 'temp_results'
RES_DIR = 'results'
# takes as argument the name of an experiment in temp_results
# produces a confusion matrix, precision and recall

cm = None
experiment_name = sys.argv[1]
feat_name = sys.argv[2]
for filename in os.listdir('{0}/{1}'.format(TEMPRES_DIR, feat_name)):
	if experiment_name not in filename:
		print "error! wrong experiment type in results"
	cm_file = open('{0}/{1}/{2}'.format(TEMPRES_DIR,feat_name,filename))
	unord_map = {}
	classes = []
	for class_num, line in enumerate(cm_file):
		line = re.split('\s+', line.strip())
		lc_class = line[-1]
		classes.append(lc_class)
		unord_map[class_num] = lc_class
	classes.sort()
	ord_map = {}
	for class_num, c in enumerate(sorted(classes)):
		ord_map[c] = class_num
	if cm is None: # create cm if necessary
		cm = [[0 for i in xrange(len(classes))] for j in xrange(len(classes))]
	# now we have the ordered classes read in the confusion matrix
	cm_file.seek(0)
	for i, line in enumerate(cm_file):
		line = re.split('\s+', line.strip())
		for j, elem in enumerate(line[:len(classes)]):
			# add to ordered class cm position
			cm[ord_map[unord_map[j]]][ord_map[unord_map[i]]] += int(elem)
	cm_file.close()
if feat_name not in os.listdir(RES_DIR):
	os.mkdir('{0}/{1}'.format(RES_DIR, feat_name))
result_filename = '{0}/{1}/{2}'.format(RES_DIR, feat_name, experiment_name + '.result')
result_file = open(result_filename, 'w')
# compute f-measure
class_fn = [0 for i in xrange(len(classes))]
class_fp = [0 for i in xrange(len(classes))]
class_tp = [0 for i in xrange(len(classes))]
class_counts = [0 for i in xrange(len(classes))]
for i in xrange(len(classes)):
	for j in xrange(len(classes)):
		if i == j:
			class_tp[i] += cm[i][j]
		else:
			class_fp[i] += cm[i][j]
			class_fn[j] += cm[i][j]
		class_counts[j] += cm[i][j]
microavg_precision = 0
microavg_recall = 0
microavg_fscore = 0
for class_num in xrange(len(classes)):
	if class_tp[class_num] + class_fp[class_num] != 0:
		microavg_precision += class_counts[class_num] * (class_tp[class_num] / \
			(1.0 * class_tp[class_num] + class_fp[class_num]))
	if class_tp[class_num] + class_fn[class_num] != 0:
		microavg_recall += class_counts[class_num] * (class_tp[class_num] / \
			(1.0 * class_tp[class_num] + class_fn[class_num]))
microavg_precision /= (1.0 * sum(class_counts))
microavg_recall /= (1.0 * sum(class_counts))
microavg_fscore = 2 * (microavg_precision * microavg_recall) / (1.0 * microavg_precision + microavg_recall)

# write number of classes
result_file.write(str(len(classes)) + '\n')

# write out the results for each class
for cn in xrange(len(classes)):
	prec = None
	recall = None

	if math.fabs(class_tp[cn] + class_fp[cn]) < 1e-10:
		prec = 0
		#print 'error:, no results for class', classes[cn]
		#continue
	else:
		prec = (1.0 * class_tp[cn] / (class_tp[cn] + class_fp[cn]))
	if math.fabs(class_tp[cn] + class_fn[cn]) < 1e-10:
		recall = 0
	else:
		recall = (1.0 * class_tp[cn] / (class_tp[cn] + class_fn[cn]))
		#print 'error:, no results for class', classes[cn]
		#continue
	
	if math.fabs(prec) < 1e-10 or math.fabs(recall) < 1e-10:
		fscore = 0.0
	else:
		fscore = (2.0 * prec * recall) / (recall + prec)
	result_file.write('{0},{1},{2},{3}\n'.format(classes[cn], prec, recall, fscore))

result_file.write('all,{0},{1},{2}\n'.format(microavg_precision, microavg_recall, microavg_fscore))	
for c, row in zip(sorted(classes), cm):
	result_file.write(c + '\t' + '\t'.join([str(obj) for obj in row]) + '\n')
	#result_file.write(str(key) + '\t' + '\t'.join([str(obj) for obj in class_rows[key]]) + '\n')
result_file.close()
