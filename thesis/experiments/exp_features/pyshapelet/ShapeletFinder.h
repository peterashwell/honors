#include "Dataset.h"
#include "Shapelet.h"
#include "TimeSeries.h"

class ShapeletFinder {
	private:
		vector<string> shapelet_type;
		vector<float> information_gain;
		vector<Shapelet> shapelets;
		static const int MAX_LEN = 100;
		static const int MIN_LEN = 20;
		static const int STEPSIZE = 20;
		float minimumDistance(Shapelet& shapelet, TimeSeries* ts);
		float informationGain(Shapelet& shapelet, Dataset& train);
	public:
		void extractShapelets(Dataset& sample, Dataset& train);
};

void ShapeletFinder::extractShapelets(Dataset& sample, Dataset& train) {
	// Iterate over sample light curves one by one, evaluating on train
	vector<TimeSeries*> sampdata = sample.getData();
	vector<TimeSeries*>::iterator ts;
	vector<string>::iterator sampled_type = sample.getTypes().begin();
	for (ts = sampdata.begin(); ts != sampdata.end(); ts++) {
		// Get subsequences
		for (int slen = MIN_LEN; slen <= MAX_LEN; slen += STEPSIZE) {
			for (int start = 0; start < (*ts)->size() - slen; start++) {
				Shapelet ns(start, slen, *ts);	// TODO create shapelet using length, start, and TimeSeries
				float ig = informationGain(ns, train); // Find information gain on training dataset
				shapelet_type.push_back(*sampled_type);
				information_gain.push_back(ig);
				shapelets.push_back(ns);
			}
		}
		sampled_type++; // iterate over the sampled class also
	}
}

float minimumDistance(Shapelet& shapelet, TimeSeries* ts) {
	return 0.0;
}

float ShapeletFinder::informationGain(Shapelet& shapelet, Dataset& train) {
	return 0.0;
}
