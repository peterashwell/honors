#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <string>
#include <iostream>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

#ifndef UTILS_H
#define UTILS_H

int getdir (string dir, vector<string> &files)
{
	DIR *dp;
	struct dirent *dirp;
	if((dp  = opendir(dir.c_str())) == NULL) {
		cout << "Error(" << errno << ") opening " << dir << endl;
		return errno;
	}

	while ((dirp = readdir(dp)) != NULL) {
		files.push_back(string(dirp->d_name));
	}
	closedir(dp);
	return 0;
}

template <class T> bool from_string(T& t, const std::string& s, std::ios_base& (*f)(std::ios_base&))
{
	std::istringstream iss(s);
	return !(iss >> f >> t).fail();
}

void split(const string &s, char delim, vector<string> &elems) {
	stringstream ss(s);
	string item;
	while(getline(ss, item, delim)) {
		elems.push_back(item);
	}
}

int readTimeSeries(string &filename, vector<float> &times, vector<float> &fluxes) {
	string path = "shapelet_train/" + filename;
	ifstream in(path.c_str());
	string line;
	// <strong class="highlight">read</strong> in each line
	while(getline(in,line)) {
		vector<string> tokens;
		split(line, '\t', tokens);
		float time;
		float flux;
		from_string<float>(time, tokens.at(0), dec);
		from_string<float>(flux, tokens.at(1), dec);
		times.push_back(time);
		fluxes.push_back(flux);
	}
}

struct MDSort {
	bool operator() (const std::pair<float, &string>& lhs, const pair<float, &string>& rhs) const {
		return (lhs.first < rhs.first);
	}
};

#endif
