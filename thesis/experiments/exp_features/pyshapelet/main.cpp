#include <string>
#include <vector>
#include <iostream>

#include "Dataset.h"
#include "Utils.h"
#include "ShapeletFinder.h"

int MIN_LENGTH = 10;
int MAX_LENGTH = 100;
int STEPSIZE = 10;

int main(int argc, char* argv[]) {
	std::string sample_dir = argv[1];
	std::string train_dir = argv[2];
	std::string out_dir = argv[3];
	
	std::cout << "sd: " << sample_dir << " td: " << train_dir << " od: " << out_dir << std::endl;	

	// Read in files in given source and training directories
	Dataset sample;
	sample.load(sample_dir);

	cout << "done loading" << endl;
	
	Dataset train;
	train.load(train_dir);

	ShapeletFinder res;
	res.extractShapelets(sample, train);
}
