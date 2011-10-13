#include "Dataset.h"
#include "Shapelet.h"
#include "TimeSeries.h"
#include <iostream>
#include <string>
#include <algorithm>
#include <math.h>
#include <ctime>

class ShapeletFinder {
	private:
		vector<string> shapelet_type;
		vector<float> information_gain;
		vector<Shapelet> shapelets;
		static const int MAX_LEN = 100;
		static const int MIN_LEN = 20;
		static const int STEPSIZE = 20;
		string ID_INDEX_FNAME;
		string DIST_INDEX_PREFIX;
		string CLASS_INDEX_FNAME;
		float minimumDistance(Shapelet& shapelet, TimeSeries* ts);
		float informationGain(Shapelet& shapelet, Dataset& train);
		void computeDistances(Dataset& sample, Dataset& train, string& outdir);
	public:
		ShapeletFinder();
		void extractShapelets(Dataset& sample, Dataset& train);;
};

ShapeletFinder::ShapeletFinder() {
		ID_INDEX_FNAME = "shapelet_ids";
		DIST_INDEX_PREFIX = "shapelet_dist_";
		CLASS_INDEX_FNAME = "shapelet_class";
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
	int SHAPELET_ID = 0; // id of shapelet we are up to

	clock_t start = clock();
	int done = 0;
	for (ts = sample.begin(); ts != sample.end(); ++ts) {
		// Get subsequences
		for (int slen = MIN_LEN; slen <= MAX_LEN; slen += STEPSIZE) {
			cout << "\tlen:" << slen << endl;
			for (int start = 0; start < (*ts)->size() - slen; ++start) {
				cout << "\t\tstart: " << start << endl;
				Shapelet ns(slen, start, *ts);	// TODO create shapelet using length, start, and TimeSeries
				float ig = informationGain(ns, train); // Find information gain on training dataset
				//shapelet_type.push_back(*sampled_type);
				//information_gain.push_back(ig);
				//shapelets.push_back(ns);
			}
		}
		cout << done << "/" << 240 << endl;
		cout << "time elapsed: << " << ((clock() - start) / (double) CLOCKS_PER_SEC) << "s" << endl;
		done += 1;
		//sampled_type++; // iterate over the sampled class also
	}
}

float ShapeletFinder::minimumDistance(Shapelet& shapelet, TimeSeries* ts, ofstream &mdfile) {
	float smallest = 999999999; // just in case for loop fails 
	bool first = true;
	int sh_len = shapelet.getLength();
	//cout << "running from 0 to " << ts->size() - shapelet.getLength() << endl;
	//cout << "shapelet length: " << sh_len << endl;
	//cout << "ts length: " << ts->size() << endl;
	for (int start = 0; start < ts->size() - shapelet.getLength(); ++start) {
		float distance = 0;
		for (int index = 0; index < min(sh_len, ts->size()); ++index) {
			distance += pow(shapelet.fluxAt(index) - ts->fluxAt(start + index), 2);
			if (!first) {
				if (distance > smallest) {
					break;
				}
			}
			first = false;
		}
		// set new winner
		if (first) {
			smallest = distance; 
		}
		else {
			if (smallest < distance) {
				smallest = distance;
			}
		}
	}
	return sqrt(smallest) / shapelet.getLength();
}

float ShapeletFinder::informationGain(Shapelet& shapelet, Dataset& train) {
	vector<TimeSeries*>::iterator ts;
	vector<pair<float, &string> > mindists; // preallocate TODO
	for (ts = train.begin(); ts != train.end(); ++ts) {
		float d = minimumDistance(shapelet, *ts);
		mindists.push_back(d);
	}
	// Now sort the mindists and class labels at the same time
	sort(mindists.begin(), mindists.end(), MDSort); // See Utils.h

	// Include as many labels of class type as possible for max inf gain, then backtrack
	vector<pair<float, &string> >::iterator md_class;
	int ofclass_seen = 0;
	int notofclass_seen = 0;
	// Until the remaining of class labels is smaller than not of class labels accumulated, search right
	for (md_class = mindists.begin(); md_class != mindists.end(); ++md_class) {
		
	}

	return 0.0;
}
