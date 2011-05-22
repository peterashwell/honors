import psyco
psyco.full()
import time
# Class for performing operations on a vector in an abstract sense
# Takes an arbitrary set of features and assigns them components of a vector to manage

class FeatureSet:
	def __init__(self, _features):
		self.features = _features
		self.feature_time = 0	

	def tag_score(self, sentence, tag, word_pos, prev_tag):
		start = time.time()
		return sum([feature.score(sentence, tag, word_pos, prev_tag) for feature in self.features])
		self.feature_time += time.time() - start

	def update_weights(self, sentence, tags_star, tags):
		start = time.time()
		for feature in self.features:
			feature.update_sentence(sentence, tags_star, tags)
		self.feature_time += time.time() - start

	def print_features(self, vector, class_offset, tags):
		for tag in tags:
			print "features for tag:", tag
			for feature in self.features:
				print "from feature", feature.id
				feature.show_weights(vector, class_offset[tag], self.feature_offset[feature.id])
				print
