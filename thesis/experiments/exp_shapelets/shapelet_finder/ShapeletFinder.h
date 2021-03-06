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
		string out_dir;
		int SHAPELET_ID; // id of shapelet we are up to
		static const int MAX_LEN = 105;
		static const int MIN_LEN = 15;
		static const int STEPSIZE = 25;
		static const int NUM_LABELS = 8; // TODO define somewhere else
		ofstream shapelet_index;
		ofstream class_index;
		float getSplitEntropy(vector<pair<float, string> >& vals, float& sepdist, string& st);
		float getSetEntropy(vector<pair<float, string> >::iterator iter, vector<pair<float, string> >::iterator end, int size, string& st);
		float minimumDistance(Shapelet& shapelet, TimeSeries* ts);
		float informationGain(Shapelet& shapelet, Dataset& train, float& sepdist);
		void computeDistances(Dataset& sample, Dataset& train);
		float getSepDist(vector<pair<float,string> >::iterator s, vector<pair<float, string> >::iterator e, int bp);
	public:
		ShapeletFinder(string& out_dir);
		~ShapeletFinder();
		void extractShapelets(Dataset& sample, Dataset& train, bool single_entropy);;
};

ShapeletFinder::ShapeletFinder(string& OUT_DIR) {
		this->out_dir = OUT_DIR;
		string ID_INDEX_FNAME = "shapelet_ids";
		string CLASS_INDEX_FNAME = "shapelet_class";
		SHAPELET_ID = 0;
		shapelet_index.open((out_dir + "/" + ID_INDEX_FNAME).c_str());
		class_index.open((out_dir + "/" + CLASS_INDEX_FNAME).c_str());
}

ShapeletFinder::~ShapeletFinder() {
	shapelet_index.close();
	shapelet_index.close();
}

void ShapeletFinder::extractShapelets(Dataset& sample, Dataset& train, bool single_entropy) {
	computeDistances(sample, train);
}

void ShapeletFinder::computeDistances(Dataset& sample, Dataset& train) {
	// Iterate over sample light curves one by one, evaluating on train
	cout << "extracting shapelets" << endl;
	vector<TimeSeries*> sampdata = sample.getData();
	vector<TimeSeries*>::iterator ts;
	//vector<string>::iterator sampled_type = sample.getTypes().begin();

	clock_t start_time = clock();
	int done = 0;
	cout << sample.size() << " time series to sample from" << endl;
	for (ts = sample.begin(); ts != sample.end(); ++ts) {
		cout << "source file: " << (*ts)->getSourceFile() << endl;
		// Get subsequences
		for (int slen = MIN_LEN; slen <= MAX_LEN; slen += STEPSIZE) {
			cout << "\tlen:" << slen << endl;
			cout << "\tsize:" << (*ts)->size() << endl;
			cout << "\tstart: " << 0 << " end:" << (*ts)->size() - slen << endl;
			for (int start = 0; start < (*ts)->size() - slen; ++start) {
				cout << "\t\tstart:" << start << endl;
				shapelet_index << SHAPELET_ID << "," << (*ts)->getSourceFile() << "," << start << "," << slen;
				//cout << "\t\tstart: " << start << endl;
				Shapelet ns(slen, start, *ts, (*ts)->getType());	// TODO create shapelet using length, start, and TimeSeries
				float sepdist;
				float ig = informationGain(ns, train, sepdist); // Find information gain on training dataset
				shapelet_index << "," << ig << "," << sepdist << endl;
				//shapelet_type.push_back(*sampled_type);
				//information_gain.push_back(ig);
				//shapelets.push_back(ns);
				SHAPELET_ID += 1; // add a new shapelet
			}
		}
		cout << done << "/" << sample.size() << endl;
		cout << "time elapsed: << " << ((clock() - start_time) / (double) CLOCKS_PER_SEC) << "s" << endl;
		done += 1;
		//sampled_type++; // iterate over the sampled class also
	}
}

float ShapeletFinder::minimumDistance(Shapelet& shapelet, TimeSeries* ts) {
	float smallest; // just in case for loop fails 
	bool first = true;
	int sh_len = shapelet.getLength();
	
	/*
	cout << "running from 0 to " << ts->size() - shapelet.getLength() << endl;
	cout << "shapelet length: " << sh_len << endl;
	cout << "shapelet type: " << shapelet.getType() << endl;
	cout << "ts class: " << ts->getType() << endl;
	cout << "ts length: " << ts->size() << endl;
*/
	for (int start = 0; start < ts->size() - shapelet.getLength(); ++start) {
		float distance = 0;
		for (int index = 0; index < min(sh_len, ts->size()); ++index) {
			distance += pow(shapelet.fluxAt(index) - ts->fluxAt(start + index), 2);
			if (!first) {
				if (distance >= smallest) {
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

float getDTWDistance(Shapelet& s, TimeSeries* ts) {
	return 0;
}


float ShapeletFinder::getSplitEntropy(vector<pair<float, string> >& vals, float& sepdist, string& st) {
	vector<pair<float, string> >::iterator iter;

	//cout << "first set" << endl;
	float best_IG = 999999999; // terrible
	float best_SD = -1;
	int best_bp = -1;
	bool first = true;
	for (int bp = 0; bp <= vals.size(); bp++) {
		int D_L_size = bp;
		int D_R_size = vals.size() - bp;
	
		// Compute set entropy of D_l and D_r
		float D_L_entropy = getSetEntropy(vals.begin(), vals.begin() + bp, D_L_size, st);	
		float D_R_entropy = getSetEntropy(vals.begin() + bp, vals.end(), D_R_size, st);
		float infgain = ((D_L_size * 1.0) / vals.size()) * D_L_entropy + ((D_R_size * 1.0) / vals.size()) * D_R_entropy; // note this is really split entropy
		//cout << "infgain at split: " << bp << " is: " << infgain << endl;
		float sepdist = getSepDist(vals.begin(), vals.end(), bp);
		bool update = false;
		if (first) {
			first = false;
			update = true;
			best_SD = sepdist;
		}
		else {
			if (infgain < best_IG) { // smaller is better (because i'm not computing the gain, just the entropy)
				update = true;
			}
			else if (infgain == best_IG) {
				if (sepdist > best_SD) {
					//cout << "found new best: " << infgain << " instead of: " << best_IG << endl;
					update = true;
				}
			}
		}
		if (update) {
			//cout << "found new best: " << infgain << " instead of: " << best_IG << endl;
			best_IG = infgain;
			best_bp = bp;
			best_SD = sepdist;
		}
	}
	//cout << "best split point: " << best_bp << endl;
	sepdist = best_SD;
	return best_IG;
}

float ShapeletFinder::getSepDist(vector<pair<float, string> >::iterator iter, vector<pair<float, string> >::iterator end, int bp) {
	float sum = 0;
	float running_sum = 0;
	int count = 0;
	while (count < bp) {
		running_sum += iter->first;
		count += 1;
		iter++;
		//cout << "added: " << iter->first << endl;
	}
	if (count != 0) {
		sum += (running_sum / count);
	}
	//cout << "count: " << count << endl;
	count = 0;
	running_sum = 0;
	while (iter != end) {
		running_sum += iter->first;
		count += 1;
		iter++;
		//cout << "added: " << iter->first << endl;
	}
	sum += running_sum / count;
	//cout << "count: " << count << endl;
	return sum;
}

float ShapeletFinder::getSetEntropy(vector<pair<float, string> >::iterator iter,
                                   vector<pair<float, string> >::iterator end, int size, string& st) {
	std::tr1::unordered_map<string, int> counts;

	while (iter != end) {
		string label = "B"; // do binary entropy
		if (st.compare(iter->second) == 0) {
			label = "A";
		}
		if ( counts.find(label) == counts.end()) {
			counts[label] = 1;
		}
		else {
			counts[label] += 1;
		}
		++iter;
	}
	float entropy_sum = 0;
	float frac;
	std::tr1::unordered_map<string, int>::iterator type_count;
	for (type_count = counts.begin(); type_count != counts.end(); ++type_count) {
		frac = type_count->second / (1.0 * size);
		entropy_sum += frac * log(frac);
	}

	return -1 * entropy_sum;
}

float ShapeletFinder::informationGain(Shapelet& shapelet, Dataset& train, float& sepdist) {
	vector<TimeSeries*>::iterator ts;
	vector<pair<float, string> > mindists; // preallocate TODO
	vector<string> filenames;
	for (ts = train.begin(); ts != train.end(); ++ts) {
		float d = minimumDistance(shapelet, *ts);
		mindists.push_back(pair<float,string>(d,(*ts)->getType()));
		filenames.push_back((*ts)->getSourceFile());
		//cout << "sh type:" << shapelet.getType() << (*ts)->getType() << "," << (*ts)->getSourceFile() << "," << d << endl;
	}
	// Now sort the mindists and class labels at the same time
	vector<pair<float, string> >::iterator iter;
	stringstream s;
	s << out_dir << "/shapelet_dist_" << SHAPELET_ID;
	cout << "writing distances to: " << out_dir << endl;
	ofstream md_file;
	int i = 0;
	md_file.open(s.str().c_str());
	for (iter = mindists.begin(); iter != mindists.end(); iter++) {
		md_file << iter->first << "," << iter->second << ',' << filenames.at(i) << endl;
		i += 1;
	}
	md_file.close();
	sort(mindists.begin(), mindists.end(), MDSortOnDistance()); // See Utils.h

	// Include as many labels of class type as possible for max inf gain, then backtrack
	/*
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
	float split_entropy = getSplitEntropy(mindists, sepdist, shapelet.getType());
	//cout << "found entropy: " << split_entropy << endl;
	return split_entropy; // TODO is the dataset entropy even needed
}
