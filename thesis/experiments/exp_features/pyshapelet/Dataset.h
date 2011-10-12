#include <vector>
#include <string>

#include "TimeSeries.h"
#include "Utils.h"

#ifndef DATASET_H
#define DATASET_H

using namespace std;

class Dataset {
	private:
		std::vector<TimeSeries*> data;
		std::vector<std::string> types;
	public:
		void load(std::string load_dir);
		std::vector<TimeSeries*>& getData();
		std::vector<std::string>& getTypes();
		Dataset();
		~Dataset();
};

Dataset::~Dataset() {
	std::vector<TimeSeries*>::iterator iter;
	for (iter = data.begin(); iter != data.end(); iter++) {
		free(*iter); // free each time series pointer
	}
}
std::vector<TimeSeries*>& Dataset::getData() {
	return data;
}
std::vector<std::string>& Dataset::getTypes() {
	return types;
}

void Dataset::load(std::string load_dir) {
	std::vector<std::string> dir_list;
	getdir(load_dir, dir_list); // See Utils.h	
	
	// Load each time series into the dataset, recording class data
	std::vector<std::string>::iterator iter;	
	for (iter = dir_list.begin(); iter != dir_list.end(); iter++) {
		TimeSeries* t = new TimeSeries();
		string type = t->load(*iter);
		data.push_back(t); // copy t into vector
		types.push_back(type); // see Utils.h	
		cout << "Type:" << type << endl;
	}
	cout << "Loaded " << data.size() << " time series" << endl;
}



#endif
