class ptFeature:
	def __init__(self, taglist_file):
		self.id = "prevtag_feature"
		self.tag_offset = {}
		taglist = open(taglist_file)
		for index, tag in enumerate(taglist):
			self.tag_offset[tag] = index
		self.tag_offset[''] = index + 1 # NULL tag
		self.size = len(self.tag_offset.keys())
		
		def score(sentence, tag, word_pos, prev_tag, vector, feature_offset, class_offset):
			# return score for previous tag for this particular class
			return vector[class_offset[tag] + feature_offset + self.tag_offset[prev_tag]]
		
		def update_sentence(sentence, tag_star, tag, vector, feature_offset, class_offset):
			for index, word in enumerate(sentence):
				if tag_star[index] != tag[index]:
					if index == 0:
						prev_tag = ''
					else:
						prev_tag = tag_star[index - 1]
					# update incorrect and correct feature vectors
					vector[class_offset[tag_star[index]] + feature_offset + self.tag_offset[prev_tag]] -= 1
					vector[class_offset[tag[index]] + feature_offset + self.tag_offset[prev_tag]] += 1

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
