#include <vector>
#include <string>
#include <tr1/unordered_map>

#include "TimeSeries.h"
#include "Utils.h"

#ifndef DATASET_H
#define DATASET_H

using namespace std;

class Dataset {
	private:
		std::vector<TimeSeries*> data;
		std::vector<std::string> types;
		std::tr1::unordered_map<std::string, int> class_counts;
	public:
		void load(std::string load_dir, int limit);
		std::vector<TimeSeries*>& getData();
		std::vector<std::string>& getTypes();
		int numOfClass(string& s);
		Dataset();
		~Dataset();
		std::vector<TimeSeries*>::iterator begin();
		std::vector<TimeSeries*>::iterator end();
		int size();
};

int Dataset::size() {
	return types.size();
}

std::vector<TimeSeries*>::iterator Dataset::begin() {
	return data.begin();
}

std::vector<TimeSeries*>::iterator Dataset::end() {
	return data.end();
}

Dataset::Dataset() {
	// nothing
}

Dataset::~Dataset() {
	std::vector<TimeSeries*>::iterator iter;
	for (iter = data.begin(); iter != data.end(); iter++) {
		free(*iter); // free each time series pointer
	}
}

int Dataset::numOfClass(string& type) {
	if ( class_counts.find(type) == class_counts.end() ) {
		return class_counts[type];
	}
	else {
		return 0;
	}
}

std::vector<TimeSeries*>& Dataset::getData() {
	return data;
}
std::vector<std::string>& Dataset::getTypes() {
	return types;
}

void Dataset::load(std::string load_dir) {
	cout << "loading from directory " << load_dir << endl;
	std::vector<std::string> dir_list;

	getdir(load_dir, dir_list); // See Utils.h	
	
	// Load each time series into the dataset, recording class data
	std::vector<std::string>::iterator iter;	

	if (limit > dir_list.size()) {
		cout << "Error: trying to load more files in directory (" << limit << 
		") than there are (" << dir_list.size() << "). Using max number of files" << endl;
		limit = dir_list.size();
	}
	cout << "Loading " << limit << "files" << endl;
	int loaded = 0;
	for (iter = dir_list.begin(); iter != dir_list.end(); iter++) {
		if (iter->compare(string(".")) == 0 or iter->compare(string("..")) == 0) {
			continue;
		}
		TimeSeries* t = new TimeSeries();
		string type = t->load(load_dir, *iter);
		data.push_back(t); // copy t into vector
		types.push_back(type); // see Utils.h	
		cout << "Type:" << type << endl;
		if ( class_counts.find(type) == class_counts.end() ) {
			class_counts[type] = 1;
		}
		else {
			class_counts[type]++;
		}
		loaded += 1;
		if (loaded == limit) {
			break;
		}
	}
	cout << "Loaded " << data.size() << " time series" << endl;
	std::tr1::unordered_map<string, int>::iterator c_count;
	for (c_count = class_counts.begin(); c_count != class_counts.end(); c_count++) {
		cout << (*c_count).first << ": " << (*c_count).second << endl;
	}
}



#endif
