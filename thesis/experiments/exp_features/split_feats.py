import os
import sys

exp_name = sys.argv[1]

# for each set of arff files, crop and split according to feature sets
feat_bounds = [] # set of featureset boundaries
feat_names = []

FEATDESC_FNAME = 'features.desc'
ARFF_DIR = 'arff'
SPLITFEAT_DIR = 'split_feats'

# find bounds of feature sets
featdesc_file = open(FEATDESC_FNAME)
feats_sofar = 0 # features seen so far (to use as start of bounds)
featlen = None # length of each feature set
featdesc = None
featname = None
subfeats = []
for line in featdesc_file:
	#print line
	line = line.strip()
	if line[0] == '#':
		if featlen is not None: # if we have seen some featureset prior
			feat_bounds.append((feats_sofar, feats_sofar + featlen))
			feats_sofar += featlen
			feat_names.append(featname)
		line = line[1:].split('\t')
		# reset for next feature set
		featlen = 0
		featname = line[0]
		featdesc = line[1]
	else:
		line = line.split('\t')
		featlen += int(line[1])
		subfeats.append(line[0])
# hardcoded 'all' features
feat_names.append('all')
feat_bounds.append((0, max([item[1] for item in feat_bounds])))
# split all files in temp_arff into directories for each feature set

for arff_fname in os.listdir('{0}/{1}'.format(ARFF_DIR, exp_name)):
	for boundnum, featname in enumerate(feat_names):
		print 'creating directory:', exp_name, featname		
		if featname not in os.listdir('{0}/{1}'.format(SPLITFEAT_DIR, exp_name)):
			os.mkdir('{0}/{1}/{2}'.format(SPLITFEAT_DIR, exp_name, featname))
		lbound = feat_bounds[boundnum][0]
		rbound = feat_bounds[boundnum][1]
		#print lbound, rbound
		# write the arff through with some cols removed
		filter_fname = '{0}/{1}/{2}/{3}'.format(SPLITFEAT_DIR, exp_name,featname, arff_fname)
		filter_file = open(filter_fname, 'w')
		# seek to @DATA section
		arff_file = open('{0}/{1}/{2}'.format(ARFF_DIR, exp_name, arff_fname))
		attr_num = 0
		data = False
		for line in arff_file:
			#print "line:", line
			if '@ATTRIBUTE' in line:
				if 'class' in line:
					filter_file.write(line)
				else:
					if featname == 'all':
						#print "writing attr:", line
						filter_file.write(line)
					else:
						if attr_num < lbound or attr_num >= rbound:
							#print "writing attr:", line
							filter_file.write(line)
						attr_num += 1
			elif data:
				line = line.strip().split(',')
				if featname == 'all':
					filter_file.write(','.join(line) + '\n')
				else:
					filter_file.write(','.join(line[0:lbound] + line[rbound:len(line) - 1]) + ',' + line[-1] + '\n')
			elif '@DATA' in line:
				data = True
				filter_file.write(line)
				#filter_file.write(','.join(line[:lbound]) + ','.join(line[rbound:]) + '\n')
			else:
				filter_file.write(line)
		filter_file.close() # write out this features arff file
		arff_file.close()
