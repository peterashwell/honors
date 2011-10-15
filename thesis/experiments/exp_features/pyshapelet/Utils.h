#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <string>
#include <iostream>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <utility>

//#define BOOST_FILESYSTEM_NO_DEPRECATED

//#include "boost/filesystem/operations.hpp"
//#include "boost/filesystem/path.hpp"
//#include "boost/progress.hpp"

using namespace std;
//namespace fs = boost::filesystem;

#ifndef UTILS_H
#define UTILS_H
/*
int boostgetdir(string dir, vector<string>& files)
{
	boost::progress_timer t( std::clog );

	fs::path full_path( fs::initial_path<fs::path>() );

	full_path = fs::system_complete( fs::path( dir ) );

	unsigned long file_count = 0;
	unsigned long dir_count = 0;
	unsigned long other_count = 0;
	unsigned long err_count = 0;

	if ( !fs::exists( full_path ) )
	{
		std::cout << "\nNot found: " << full_path.file_string() << std::endl;
		return 1;
	}

	if ( fs::is_directory( full_path ) )
	{
		std::cout << "\nIn directory: "
							<< full_path.directory_string() << "\n\n";
		fs::directory_iterator end_iter;
		for ( fs::directory_iterator dir_itr( full_path );
					dir_itr != end_iter;
					++dir_itr )
		{
			try
			{
				if ( fs::is_directory( dir_itr->status() ) )
				{
					++dir_count;
					std::cout << dir_itr->path().filename() << " [directory]\n";
				}
				else if ( fs::is_regular_file( dir_itr->status() ) )
				{
					++file_count;
					files.push_back(dir_itr->path().filename());
					std::cout << dir_itr->path().filename() << "\n";
				}
				else
				{
					++other_count;
					std::cout << dir_itr->path().filename() << " [other]\n";
				}

			}
			catch ( const std::exception & ex )
			{
				++err_count;
				std::cout << dir_itr->path().filename() << " " << ex.what() << std::endl;
			}
		}
		std::cout << "\n" << file_count << " files\n"
							<< dir_count << " directories\n"
							<< other_count << " others\n"
							<< err_count << " errors\n";
	}
	else // must be a file
	{
		std::cout << "\nFound: " << full_path.file_string() << "\n";		
	}
}*/

int getdir (string dir, vector<string> &files)
{
	DIR *dp;
	struct dirent *dirp;
	cout << dir.c_str() << endl;
	if((dp  = opendir(dir.c_str())) == NULL) {
		perror("opendir");
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
