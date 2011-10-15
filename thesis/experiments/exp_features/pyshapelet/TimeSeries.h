#include <vector>
#include <string>

#include "Utils.h"

#ifndef TIMESERIES_H
#define TIMESERIES_H

using namespace std;

class TimeSeries {
	private:
		string type;
		string source_file;
		vector<float> times;
		vector<float> flux;
		vector<bool> missing;
	public:
		string load(string& path, string &fname);
		int size();
		string& getType();
		float fluxAt(int index);
		string& getSourceFile();
};

int TimeSeries::size() {
	return times.size();
}

string& TimeSeries::getType() {
	return type;
}

string& TimeSeries::getSourceFile() {
	return source_file;
}

float TimeSeries::fluxAt(int index) {
	return flux.at(index);
}

string TimeSeries::load(string& path, string &fname) {
	source_file = path + "/" + fname;
	cout << "reading file: " << source_file << endl;;
	readTimeSeries(source_file, times, flux); // TODO missing data 	
	vector<string> fname_split;
	split(fname, '_', fname_split);
	type = fname_split.at(0);
	return fname_split.at(0); // return class type
}

#endif
