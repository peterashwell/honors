import os

# for each set of arff files, crop and split according to feature sets
feat_bounds = [] # set of featureset boundaries
feat_names = []

FEATDESC_FNAME = 'features.desc'
ARFF_DIR = 'temp_arff'
SPLITFEAT_DIR = 'temp_splitfeats'

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
#print feat_bounds	
# hardcoded 'all' features
feat_names.append('all')
feat_bounds.append((0, max([item[1] for item in feat_bounds])))
#print feat_names
#print feat_bounds
# split all files in temp_arff into directories for each feature set
for arff_fname in os.listdir(ARFF_DIR):
	for boundnum, featname in enumerate(feat_names):
		
		lbound = feat_bounds[boundnum][0]
		rbound = feat_bounds[boundnum][1]
		#print lbound, rbound
		# write the arff through with some cols removed
		if featname not in os.listdir(SPLITFEAT_DIR):
			os.mkdir('{0}/{1}'.format(SPLITFEAT_DIR, featname))
		filter_fname = '{0}/{1}/{2}'.format(SPLITFEAT_DIR, featname, arff_fname)
		filter_file = open(filter_fname, 'w')
		# seek to @DATA section
		arff_file = open(ARFF_DIR + '/' + arff_fname)
		attr_num = 0
		data = False
		for line in arff_file:
			if '@ATTRIBUTE' in line:
				if 'class' in line:
					filter_file.write(line)
				else:
					if attr_num >= lbound and attr_num < rbound:
						filter_file.write(line)
					attr_num += 1
			elif data:
				line = line.strip().split(',')
				filter_file.write(','.join(line[lbound:rbound]) + ',' + line[-1] + '\n')
			elif '@DATA' in line:
				data = True
				filter_file.write(line)
				#filter_file.write(','.join(line[:lbound]) + ','.join(line[rbound:]) + '\n')
			else:
				filter_file.write(line)
		filter_file.close() # write out this features arff file
arff_file.close()
