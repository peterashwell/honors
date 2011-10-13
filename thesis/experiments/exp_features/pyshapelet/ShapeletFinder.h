#include "Dataset.h"
#include "Shapelet.h"
#include "TimeSeries.h"
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <math.h>
#include <ctime>
#include <utility>

class ShapeletFinder {
	private:
		vector<string> shapelet_type;
		vector<float> information_gain;
		vector<Shapelet> shapelets;
		int SHAPELET_ID; // id of shapelet we are up to
		static const int MAX_LEN = 100;
		static const int MIN_LEN = 20;
		static const int STEPSIZE = 20;
		static const int NUM_LABELS = 8; // TODO define somewhere else
		ofstream shapelet_index;
		ofstream class_index;
		float getSplitEntropy(vector<pair<float, string> >& vals, int bp);
		float getSetEntropy(vector<pair<float, string> >::iterator iter, vector<pair<float, string> >::iterator end, int size);
		float minimumDistance(Shapelet& shapelet, TimeSeries* ts);
		float informationGain(Shapelet& shapelet, Dataset& train);
		void computeDistances(Dataset& sample, Dataset& train, string& outdir);
		float getSepDist(vector<pair<float,string> >::iterator s, vector<pair<float, string> >::iterator e, int bp);
	public:
		ShapeletFinder();
		~ShapeletFinder();
		void extractShapelets(Dataset& sample, Dataset& train);;
};

ShapeletFinder::ShapeletFinder() {
		string ID_INDEX_FNAME = "shapelet_ids";
		string CLASS_INDEX_FNAME = "shapelet_class";
		SHAPELET_ID = 0;
		shapelet_index.open(string("found_shapelets/" + ID_INDEX_FNAME).c_str());
		class_index.open(string("found_shapelets/" + CLASS_INDEX_FNAME).c_str());
}

ShapeletFinder::~ShapeletFinder() {
	shapelet_index.close();
	shapelet_index.close();
}

void ShapeletFinder::extractShapelets(Dataset& sample, Dataset& train) {
	string out_dir = "";
	computeDistances(sample, train, out_dir);
}

void ShapeletFinder::computeDistances(Dataset& sample, Dataset& train, string& outdir) {
	// Iterate over sample light curves one by one, evaluating on train
	cout << "extracting shapelets" << endl;
	vector<TimeSeries*> sampdata = sample.getData();
	vector<TimeSeries*>::iterator ts;
	//vector<string>::iterator sampled_type = sample.getTypes().begin();

	clock_t start = clock();
	int done = 0;
	for (ts = sample.begin(); ts != sample.end(); ++ts) {
		// Get subsequences
		for (int slen = MIN_LEN; slen <= MAX_LEN; slen += STEPSIZE) {
			cout << "\tlen:" << slen << endl;
			for (int start = 0; start < (*ts)->size() - slen; ++start) {
				shapelet_index << SHAPELET_ID << "," << (*ts)->getSourceFile() << "," << start << "," << slen;
				cout << "\t\tstart: " << start << endl;
				Shapelet ns(slen, start, *ts, (*ts)->getType());	// TODO create shapelet using length, start, and TimeSeries
				float ig = informationGain(ns, train); // Find information gain on training dataset
				shapelet_index << "," << ig << endl;
				//shapelet_type.push_back(*sampled_type);
				//information_gain.push_back(ig);
				//shapelets.push_back(ns);
				SHAPELET_ID += 1; // add a new shapelet
			}
		}
		cout << done << "/" << 240 << endl;
		cout << "time elapsed: << " << ((clock() - start) / (double) CLOCKS_PER_SEC) << "s" << endl;
		done += 1;
		//sampled_type++; // iterate over the sampled class also
	}
}

float ShapeletFinder::minimumDistance(Shapelet& shapelet, TimeSeries* ts) {
	float smallest = 999999999; // just in case for loop fails 
	bool first = true;
	int sh_len = shapelet.getLength();
	//cout << "running from 0 to " << ts->size() - shapelet.getLength() << endl;
	//cout << "shapelet length: " << sh_len << endl;
	//cout << "ts length: " << ts->size() << endl;
	//cout << "ts pointer:" << ts << endl;
	for (int start = 0; start < ts->size() - shapelet.getLength(); ++start) {
		float distance = 0;
		for (int index = 0; index < min(sh_len, ts->size()); ++index) {
			distance += pow(shapelet.fluxAt(index) - ts->fluxAt(start + index), 2);
			if (!first) {
				if (distance > smallest) {
					break;
				}
			}
		}
		// set new winner
		if (first) {
			smallest = distance;
			first = false; 
		}
		else {
			if (distance < smallest) {
				smallest = distance;
			}
		}
	}
	//cout << "distance:" << smallest << endl;;
	return sqrt(smallest) / shapelet.getLength();
}

float ShapeletFinder::getSplitEntropy(vector<pair<float, string> >& vals, int breakpoint) {
	vector<pair<float, string> >::iterator iter;

	//cout << "first set" << endl;
	bool first = true;
	float best;
	float bestsepdist;
	float infgain;
	for (int bp = 0; bp <= vals.size(); bp++) {
		int D_L_size = bp;
		int D_R_size = vals.size() - bp;
		
		//sort(vals.begin() + bp, vals.end(), MDSortOnLabels()); // + breakpoint + 1; vals.end(); MDSortOnLabels());
		//sort(vals.begin(), vals.begin() + bp, MDSortOnLabels()); // See Utils.h
	
		// start at start until hitting breakpoint
		float D_L_entropy = getSetEntropy(vals.begin(), vals.begin() + bp, D_L_size);
		//cout << "second set" << endl;
		// start at bp and work across
		float D_R_entropy = getSetEntropy(vals.begin() + bp, vals.end(), D_R_size);
		//cout << "D_L: " << D_L_entropy << " D_R: " << D_R_entropy << endl;
		float infgain = ((D_L_size * 1.0) / vals.size()) * D_L_entropy + ((D_R_size * 1.0) / vals.size()) * D_R_entropy;
		if (first) {
			best = infgain;
			bestsepdist = getSepDist(vals.begin(), vals.end(), bp);
		}
		else {
			if (infgain > best) {
				infgain = best;
			}
			else if (infgain == best) {
				float sepdist = getSepDist(vals.begin(), vals.end(), bp);
				if (sepdist > bestsepdist) {
					best = infgain;
					bestsepdist = sepdist;
				}
			}
		}
	}
	return best;
}

float ShapeletFinder::getSepDist(vector<pair<float, string> >::iterator iter, vector<pair<float, string> >::iterator end, int bp) {
	float sum = 0;
	float running_sum = 0;
	int count = 0;
	while (iter != end) {
		if (count == bp) {
			sum += (1.0 * running_sum) / count;
			count = 0;
		}
		running_sum += iter->first;
		++count; 
		++iter;
	}
	sum += (1.0 * running_sum) / count;
	return sum;
}

float ShapeletFinder::getSetEntropy(vector<pair<float, string> >::iterator iter,
                                   vector<pair<float, string> >::iterator end, int size) {
	std::tr1::unordered_map<string, float> counts;
	while (iter != end) {
		if ( counts.find(iter->second) == counts.end()) {
			counts[iter->second] = 1;
		}
		else {
			counts[iter->second] += 1;
		}
		++iter;
	}
	float entropy_sum = 0;
	float frac;
	std::tr1::unordered_map<string, float>::iterator type_count;
	for (type_count = counts.begin(); type_count != counts.end(); ++type_count) {
		frac = type_count->second / (1.0 * size);
		entropy_sum += frac * log(frac);
	}

	return -1 * entropy_sum;
}

float ShapeletFinder::informationGain(Shapelet& shapelet, Dataset& train) {
	vector<TimeSeries*>::iterator ts;
	vector<pair<float, string> > mindists; // preallocate TODO
	for (ts = train.begin(); ts != train.end(); ++ts) {
		float d = minimumDistance(shapelet, *ts);
		mindists.push_back(pair<float,string>(d,(*ts)->getType()));
	}
	// Now sort the mindists and class labels at the same time
	sort(mindists.begin(), mindists.end(), MDSortOnDistance()); // See Utils.h
	vector<pair<float, string> >::iterator iter;
	stringstream s;
	s << "found_shapelets/shapelet_dist_" << SHAPELET_ID;
	ofstream md_file;
	md_file.open(s.str().c_str());
	for (iter = mindists.begin(); iter != mindists.end(); iter++) {
		md_file << iter->first << "," << iter->second << endl;
	}
	md_file.close();

	// Include as many labels of class type as possible for max inf gain, then backtrack
	vector<pair<float, string> >::iterator md_class;
	int ofclass_seen = 0;
	int notofclass_seen = 0;
	int breakpoint = 0;
	// Until the remaining of class labels is smaller than not of class labels accumulated, search right
	string shapelet_class(shapelet.getType());
	int vec_index = 0;
	float best_ratio = 0.0;
	float ratio;
	//cout << "shapelet class: " << shapelet_class << endl;
	/*
	for (md_class = mindists.begin(); md_class != mindists.end(); ++md_class) {
		//cout << "class: " << md_class->second << " comparison " << md_class->second.compare(shapelet_class) << endl;
		if (md_class->second.compare(shapelet_class) == 0) {
			ofclass_seen += 1;
			if (notofclass_seen == 0) {
				ratio = 1;
			}
			else {
				ratio = ofclass_seen / (vec_index + 1.0);
			}
			//cout << "ratio: " << ratio << " ocs: " << ofclass_seen << " vi1 "  << vec_index + 1 << endl;
			if (ratio >= best_ratio) {
				breakpoint = vec_index + 1; // breakpoint includes index-th element in slice notation
				best_ratio = ratio;
			}
			//cout << "best: " << best_ratio << " breakpoint: " << breakpoint << endl;
		}
		else {
			notofclass_seen += 1;
		}
		if (notofclass_seen >= train.numOfClass(shapelet.getType()) - ofclass_seen) {
			break;
		}
		//cout << "(" << md_class->first << " " << md_class->second << ") "; // do nothing
		vec_index += 1; // current index searched to
	} */
	//cout << endl;
	//cout << "broke with ofs: " << ofclass_seen << " " << " nofs: " << notofclass_seen << " breakpoint " << breakpoint << endl;
	// Now compute information gain by sorting on the labels
	float split_entropy = getSplitEntropy(mindists, breakpoint);
	//cout << "found entropy: " << split_entropy << endl;
	return split_entropy; // TODO is the dataset entropy even needed
}
