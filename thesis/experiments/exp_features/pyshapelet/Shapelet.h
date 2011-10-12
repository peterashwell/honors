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
};

Shapelet::Shapelet(int l, int s, TimeSeries* tsp) {
	length = l;
	start = s;
	ts = tsp;
}
