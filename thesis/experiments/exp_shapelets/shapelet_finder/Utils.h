#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <string>
#include <iostream>
#include <algorithm>
#include <vector>
#include <fstream>
#include <sstream>
#include <utility>

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
		cout << "found" << dirp->d_name << endl;
		files.push_back(string(dirp->d_name));
	}
	closedir(dp);
	return 0;
}

int readindex(string path, vector<string> &filenames) {
	string line;
	ifstream myfile (path.c_str());
	if (myfile.is_open())
	{
		while ( myfile.good() ) {
		getline (myfile,line);
		string::iterator end_pos = std::remove(line.begin(), line.end(), '\n');
		line.erase(end_pos, line.end());
		filenames.push_back(line);
		cout << line << endl;
		}
		myfile.close();
	}
	else cout << "Unable to open file"; 
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

int readTimeSeries(string &path, vector<float> &times, vector<float> &fluxes) {
	ifstream in(path.c_str());
	string line;
	// <strong class="highlight">read</strong> in each line
	while(getline(in,line)) {
		vector<string> tokens;
		split(line, '\t', tokens);
		if (tokens.size() == 0) {
			return false;
		}
		float time;
		float flux;
		from_string<float>(time, tokens.at(0), dec);
		from_string<float>(flux, tokens.at(1), dec);
		times.push_back(time);
		fluxes.push_back(flux);
	}
	return true;
}

struct MDSortOnDistance {
	bool operator() (const pair<float, string>& lhs, const pair<float, string>& rhs) {
		return (lhs.first < rhs.first);
	}
};

struct MDSortOnLabels {
	bool operator() (const pair<float, string>& lhs, const pair<float, string>& rhs) {
		return (lhs.second.compare(rhs.second) < 0);
	}
};

#endif
