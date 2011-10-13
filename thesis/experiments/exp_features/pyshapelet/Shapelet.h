#include <string>

#include "Timeseries.h"

class Shapelet {
	private:
		std::string type; // source type
		int length;
		int start;
		TimeSeries* ts;
	public:
		Shapelet(int l, int s, TimeSeries* tsp);
		int getLength();
		float fluxAt(int index); // find flux in underlying time sequence adjusting for shapelet start
};

int Shapelet::getLength() {
	return length;
}

float Shapelet::fluxAt(int index) {
	return ts->fluxAt(index + start);
}

Shapelet::Shapelet(int l, int s, TimeSeries* tsp) {
	length = l;
	start = s;
	ts = tsp;
}
