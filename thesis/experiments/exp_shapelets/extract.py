# Script to extract features
#		1) Store in corresponding directory to crossfold split (either hybrid or symmetric)
#		2) Keep organised by feature name as well

import sys

# Configure
CONFIG_FILE = "config"
configs = eval(open(CONFIG_FILE).read().strip())
CF_DIR = configs["CROSSFOLD_DIR"]
LC_DIR = configs["LIGHTCURVE_DIR"]

# Read features.config file in experiment directory and extract features
# Features stored as:
#	features/
#		<featurename>/ -- Might include some config info (eg length)
#			<sourcedirectory>/ -- May be a complex term for shapelets
#				train0
#				test0
#				...

FEATURE_CONFIG_FILE = "features.config"
EXP_DIR = sys.argv[1]
print "experiment directory:", EXP_DIR

# Read "compute" section of the experiment and extract all
feature_config = open("{0}/{1}".format(EXP_DIR, FEATURE_CONFIG_FILE))
compute = True
for line in feature_config:
	if line.strip() == "#compute":
		continue
	if line.strip() == "#display":
		compute = False
		continue
	
	# Extract features using given parameters and store according to directory structure above
	line = line.strip().split(',')
	feature_func = line[0]
	args = line[1]
			
