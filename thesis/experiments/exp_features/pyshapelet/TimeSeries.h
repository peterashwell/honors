#include <vector>
#include <string>

#include "Utils.h"

#ifndef TIMESERIES_H
#define TIMESERIES_H

using namespace std;

class TimeSeries {
	private:
		string type;
		vector<float> times;
		vector<float> flux;
		vector<bool> missing;
	public:
		string load(string &fname);
		int size();
};

int TimeSeries::size() {
	return times.size();
}

string TimeSeries::load(string &fname) {
	readTimeSeries(fname, times, flux); // TODO missing data 	
	vector<string> fname_split;
	split(fname, '_', fname_split);
	return fname_split.at(0); // return class type
}
#endif
