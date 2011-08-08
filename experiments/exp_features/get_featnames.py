FEATDESC_FNAME = 'features.desc'
FEATNAME_FNAME = 'features.names'

featdesc_file = open(FEATDESC_FNAME)
featname_file = open(FEATNAME_FNAME, 'w')
for line in featdesc_file:
	if line[0] == '#':
		featname = line[1:].strip().split('\t')[0]
		featname_file.write(featname + '\n')
featname_file.close()
featdesc_file.close()
