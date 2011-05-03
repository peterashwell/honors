import random
import math

class_weights = {}
raw_annotations = open("comp5046-labels.tsv")
first = True
for line in raw_annotations:
	if first:
		first = False
		continue # skip first line
	line = line.strip().split('\t')
	title = line[0]
	category = line[2]
	uncertain = line[3]
	score = None # score to add that we think this is the correct class
	if eval(uncertain):
		score = 0.5
	else:
		score = 1
	if title in class_weights.keys():
		if category in class_weights[title].keys():
			class_weights[title][category] += score
		else:
			class_weights[title][category] = score
	else:
		new_dict = {}
		new_dict[category] = score
		class_weights[title] = new_dict
raw_annotations.close()

correct_out = open("correct_class.csv", 'w')
for title in class_weights.keys():
	best = None
	best_score = None
	for category in class_weights[title].keys():
		if best is None:
			best_score = class_weights[title][category]
			best = category
		else:
			score = class_weights[title][category]
			if math.fabs(score - best_score) < 1e-10:
				if random.random() > 0.5:
					best_score = score
					best = category
			elif score > best_score:
				best_score = score
				best = category
	correct_out.write(','.join([title, best]) + "\n")
correct_out.close()

			

