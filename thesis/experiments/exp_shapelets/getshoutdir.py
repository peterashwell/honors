import getopt, sys
opts, args = getopt.getopt(sys.argv[1:], "dac:s:t:T:S:")
output = None
verbose = False
sample_dir = "sample_dir"
train_dir = "train_dir"
crossfold = -1
use_dtw = False
use_md = True
use_scaling = False
train_amt = -1
samp_amt = -1
for o, a in opts:
	if o == '-s':
		sample_dir = a;
	if o == '-t':
		train_dir = a;
	elif o == '-c':
		crossfold = a;
	elif o == '-d':
		use_dtw = True;
		use_md = False;
	elif o == '-a':
		use_scaling = True;
	elif o == '-T':
		train_amt = a;
	elif o == '-S':
		samp_amt = a;
dir = "shapelets/" + sample_dir + "-" + train_dir + "-S" + str(samp_amt) + "-T" + str(train_amt)
if use_dtw:
	dir += "-DTW"
else:
	dir += "-MD"
print dir
