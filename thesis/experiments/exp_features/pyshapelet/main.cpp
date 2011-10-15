#include <string>
#include <vector>
#include <iostream>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>


#include "Dataset.h"
#include "Utils.h"
#include "ShapeletFinder.h"

int MIN_LENGTH = 10;
int MAX_LENGTH = 100;
int STEPSIZE = 10;

int main(int argc, char* argv[]) {
	//std::string sample_dir = argv[1];
	//std::string train_dir = argv[2];
	//std::string out_dir = argv[3];
	
	string sample_dir = "nosample";
	string train_dir = "notrain";
	std::cout << "sd: " << sample_dir << " td: " << train_dir << endl; //" od: " << out_dir << std::endl;	
	string crossfold = "-1"; // extract crossfolds one at a time for hacky parallellism
	bool use_dtw = false; // use dynamic time warping as distance measure
	bool use_md = true; // use minimum distance as distance measure
	bool use_scaling = false; // use scaling in distance measure
	string train_amt = "-1"; // number of training light curves to use from train
	string samp_amt = "-1"; // number of sample light cruves to use
	
	char c;
	while ((c = getopt (argc, argv, "dac:s:t:T:S:")) != -1)
	{
		cout << "c:" << c << endl;
		switch (c)
		{
			case 's':
				cout << "s found" << endl;
				sample_dir = optarg;
				break;
			case 't':
				cout << "t found" << endl;
				train_dir = optarg;
				break;
			case 'c':
				cout << "c found" << endl;
				crossfold = optarg;
				break;
			case 'd':
				cout << "d found" << endl;
				use_dtw = true;
				use_md = false;
				break;
			case 'a':
				cout << "a found" << endl;
				use_scaling = true;
				break;
			case 'T':
				cout << "T found" << endl;
				train_amt = optarg;
				break;
			case 'S':
				cout << "S found" << endl;
				samp_amt = optarg;
				break;
			case '?':
				if (optopt == 'c')
					fprintf (stderr, "Option -%c requires an argument.\n", optopt);
				else if (isprint (optopt))
					fprintf (stderr, "Unknown option `-%c'.\n", optopt);
				else
					fprintf (stderr,"Unknown option character `\\x%x'.\n",optopt);
					return 1;
			default:
				abort ();
		}
	}

	cout << "crossfold" << crossfold << endl;
	cout << "sd: " << sample_dir << " td: " << train_dir << " cf: " << crossfold << " md: " << use_md << " dtw: " << use_dtw << " ta: " << train_amt
	  << " sa: " << samp_amt << endl;

	// Files to draw shapelets from and train on (sample and train)
	string sample_cf_dir = "crossfold/" + sample_dir;
	string train_cf_dir = "crossfold/" + train_dir;
	sample_cf_dir = sample_cf_dir + "/cf" + crossfold;
	train_cf_dir = train_cf_dir + "/cf" + crossfold;
	
	string out_dir = "shapelets/" + sample_dir + "-" + train_dir;
	if (use_dtw) {
		out_dir = out_dir + "-DTW";
	}
	else {
		out_dir = out_dir + "-MD";
	}
	out_dir = out_dir + "/cf" + crossfold;

	cout << "train: " << train_cf_dir << endl;
	cout << "sample: " << sample_cf_dir << endl;
	cout << "out: " << out_dir << endl;
	// Read in files in given source and training directories
	Dataset sample;
	//sample.load(sample_cf_dir, limit);

	cout << "done loading" << endl;
	
	Dataset train;
	//train.load(train_dir, limit);

	ShapeletFinder res;
	//res.extractShapelets(sample, train);
}
