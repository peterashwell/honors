import os
classes = ['ESE', 'Flare', 'Novae', 'Noise', 'SNe', 'IDV']
general_metrics_out = open('processed/general_metrics.tex', 'w')
general_metrics_out.write('\\hline Experiment conditions & Precision & Recall & F-Score \\\\ \\hline \n') 
for file in os.listdir('results/'):
	extension = file.split('.')[1]
	print "processing experiment:", file.split('.')[0]
	specific_metrics_out = open('processed/' + file.split('.')[0] + '.analysis', 'w')
	experiment_cm_out = open('processed/' + file.split('.')[0] + '.cm', 'w')
	# Experiment specific metrics (and cm) as well as general metrics
	if extension == 'incorrect':
		incorr_file = open('results/' + file)
		cm = {} # cm for this 
		for c in classes:
			new_dict = {}
			for c_other in classes:
				new_dict[c_other] = 0
			cm[c] = new_dict
		for test_case in incorr_file:
			# Break up the line
			test_case = test_case.strip().split(',')
			test_file = test_case[0]
			test_class = test_case[0].split('_')[0]
			classified_as = test_case[1]
			nearest_files = test_case[2:]
			#print test_file, test_class, classified_as, nearest_files
			if classified_as not in cm.keys():
				new_dict = {}
				new_dict[test_class] = 1
				cm[classified_as] = new_dict
			else:
				if test_class not in cm[classified_as].keys():
					cm[classified_as][test_class] = 1
				else:
					cm[classified_as][test_class] += 1
				
			# If not equal, produce a plot of the nearest neighbors to compare to
			pass # TODO this
		for tc in classes:
			experiment_cm_out.write(tc[:3])
			for fc in classes:
				experiment_cm_out.write(' \t& ' + str(cm[fc][tc]))
			experiment_cm_out.write('\n')
		experiment_cm_out.close()
		class_count = {}
		class_correct = {}
		clsfas_count = {}
		for c in classes:
			class_count[c] = 0
			class_correct[c] = 0
			clsfas_count[c] = 0	
		for tc in classes:
			for fc in classes:
				class_count[fc] += cm[fc][tc]
				clsfas_count[tc] += cm[fc][tc]
				if tc == fc:
					class_correct[tc] += cm[fc][tc]
		microavg_prec = 0.0
		microavg_recall = 0.0
		microavg_fscore = 0.0
		specific_metrics_out.write('\\hline Class & Precision & Recall & F-Score \\\\ \\hline \n')
		for c in classes:
			precision = 'N/A'
			if clsfas_count[c] != 0:
				precision = class_correct[c] / (clsfas_count[c] * 1.0)
			recall = 'N/A'
			if class_count[c] != 0:
				recall = class_correct[c] / (class_count[c] * 1.0)
			fscore = 'N/A'
			if precision != 'N/A' and recall != 'N/A':
				if precision + recall != 0:
					fscore = 2 * (precision * recall) / (precision + recall)
				else:
					fscore = 0
			specific_metrics_out.write(c[:3] + ' & ' + str(precision) + ' & ' + str(recall) + ' & ' + str(fscore) + ' \\\\ \n')
			if precision != 'N/A':
				microavg_prec += class_count[c] * precision
			if recall != 'N/A':
				microavg_recall += class_count[c] * recall
			if fscore != 'N/A':
				microavg_fscore += class_count[c] * fscore
		total_classes = 600.0
		microavg_prec /= total_classes
		microavg_recall /= total_classes
		microavg_fscore /= total_classes
		specific_metrics_out.write('microaverages: & ' + str(round(microavg_prec, 3)) + ' & ' + str(round(microavg_recall,3)) + ' & ' + str(round(microavg_fscore, 3)) + ' \\\\ \n')
		specific_metrics_out.close()
		general_metrics_out.write(file.split('.')[0] + ' & ' + str(round(microavg_prec, 3)) + ' & ' + str(round(microavg_recall,3)) + ' & ' + str(round(microavg_fscore,3)) + ' \\\\ \n')
general_metrics_out.close()
