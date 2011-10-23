import getopt, sys
def getshstoredir(commands):
	opts, args = getopt.getopt(commands.split(' '), "odac:s:t:T:S:b:")
	print "commands:", commands
	output = None
	verbose = False
	sample_path = "sample_path"
	train_path = "train_path"
	crossfold = -1
	use_dtw = False
	use_md = True
	use_scaling = False
	train_amt = -1
	samp_amt = -1
	best_amt = -1
	print "found optargs:", opts
	for o, a in opts:
		if o == '-s':
			sample_path = a;
		if o == '-t':
			train_path = a;
		elif o == '-c':
			crossfold = a;
		elif o == '-d':
			use_dtw = True;
			use_md = False;
		elif o == '-a':
			use_scaling = True;
		elif o == '-T':
			print "FOUND TRAIN AMT:", a
			train_amt = a;
		elif o == '-S':
			samp_amt = a;
	path = sample_path + "-" + train_path + "-S" + str(samp_amt) + "-T" + str(train_amt)
	if use_dtw:
		path += "-DTW"
	else:
		path += "-MD"
	# TODO add entropy measure computations
	return "shapelets/" + path

def getshfeatdir(commands):
	opts, args = getopt.getopt(commands.split(' '), "odac:s:t:T:S:b:")
	print "commands:", commands
	output = None
	verbose = False
	sample_path = "sample_path"
	train_path = "train_path"
	crossfold = -1
	use_dtw = False
	use_md = True
	use_scaling = False
	train_amt = -1
	samp_amt = -1
	best_amt = -1
	print "found optargs:", opts
	for o, a in opts:
		if o == '-s':
			sample_path = a;
		if o == '-t':
			train_path = a;
		elif o == '-c':
			crossfold = a;
		elif o == '-d':
			use_dtw = True;
			use_md = False;
		elif o == '-a':
			use_scaling = True;
		elif o == '-T':
			print "FOUND TRAIN AMT:", a
			train_amt = a;
		elif o == '-S':
			samp_amt = a;
		elif o == '-b':
			best_amt = a;
	path = sample_path + "-" + train_path + "-S" + str(samp_amt) + "-T" + str(train_amt)
	if use_dtw:
		path += "-DTW"
	else:
		path += "-MD"
	# TODO add entropy measure computations
	if best_amt != -1: # For feature extraction only
		path += "-b" + str(best_amt)
	return [path, use_dtw, use_md, best_amt]




if __name__ == '__main__':
	print getshstoredir(' '.join(sys.argv[1:]))
