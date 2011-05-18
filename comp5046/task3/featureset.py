# Class for performing operations on a vector in an abstract sense
# Takes an arbitrary set of features and assigns them components of a vector to manage

class FeatureSet:
	def __init__(self, _features):
		self.features = _features
		self.feature_offset = {}
		offset = 0
		for feature in self.features:
			self.feature_offset[feature.id] = offset
			offset += feature.size
		self.total_size = offset
		
	# use each feature class to update the vector given the context
	def tag_score(sentence, tag, word_pos, prev_tag, vector):
		return sum([feature.score(sentence, tag, word_pos, prev_tag, vector, self.feature_offset[feature.id]) for feature in self.features])
	
	def update_weights(sentence, word_pos, tag_star, tag, vector):
		for feature in self.features:
			feature.update(sentence, tag_star, tag, vector, self.feature_offset[feature.id])
