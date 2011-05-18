class cwFeature:
	def __init__(self, wordlist_file):
		self.id = "curword_feature"
		self.word_offset = {}
		wordlist = open(wordlist_file)
		for index, word in enumerate(wordlist):
			self.word_offset[word] = index
		self.size = len(self.word_offset.keys())

	def score(sentence, tag, word_pos, prev_tag, vector, feature_offset, class_offset):
		return vector[class_offset[tag] + feature_offset + self.word_offset[sentence[word_pos]]]
	
	def update_sentence(sentence, tag_star, tag, vector, feature_offset, class_offset):
		for index, word in enumerate(sentence):
			if tag_star[index] != tag[index]:
				vector[class_offset[tag_star[index]] + feature_offset + self.word_offset[word]] -= 1
				vector[class_offset[tag[index]] + feature_offset + self.word_offset[word]] += 1
