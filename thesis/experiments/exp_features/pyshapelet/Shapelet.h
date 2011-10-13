#include <string>

#include "Timeseries.h"

class Shapelet {
	private:
		std::string type; // source type
		int length;
		int start;
		TimeSeries* ts;
	public:
		Shapelet(int l, int s, TimeSeries* tsp, string& t);
		int getLength();
		string& getType();
		float fluxAt(int index); // find flux in underlying time sequence adjusting for shapelet start
};

int Shapelet::getLength() {
	return length;
}
string& Shapelet::getType() {
	return type; 
}

float Shapelet::fluxAt(int index) {
	return ts->fluxAt(index + start);
}

Shapelet::Shapelet(int l, int s, TimeSeries* tsp, string& t) {
	length = l;
	start = s;
	ts = tsp;
	type = t;
}
