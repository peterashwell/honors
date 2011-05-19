import psyco
psyco.full()

class ptFeature:
	def __init__(self, taglist_file):
		self.id = "prevtag_feature"
		self.tag_offset = {}
		taglist = open(taglist_file)
		for index, tag in enumerate(taglist):
			self.tag_offset[tag.strip()] = index
		self.tag_offset[''] = index + 1 # NULL tag
		self.size = len(self.tag_offset.keys())
		
	def score(self, sentence, tag, word_pos, prev_tag, vector, feature_offset_val, class_offset):
		#print "scoring", sentence, tag, word_pos, prev_tag, len(vector), feature_offset_val
		# return score for previous tag for this particular class
		#print self.tag_offset.keys()
		return vector[class_offset[tag] + feature_offset_val + self.tag_offset[prev_tag]]
		
	def update_sentence(self, sentence, tag_star, tag, vector, feature_offset_val, class_offset):
		for index, word in enumerate(sentence):
			if tag_star[index] != tag[index]:
				if index == 0:
					prev_tag = ''
				else:
					prev_tag = tag_star[index - 1]
				# update incorrect and correct feature vectors
				vector[class_offset[tag_star[index]] + feature_offset_val + self.tag_offset[prev_tag]] -= 1
				vector[class_offset[tag[index]] + feature_offset_val + self.tag_offset[prev_tag]] += 1

class cwFeature:
	def __init__(self, wordlist_file):
		self.id = "curword_feature"
		self.word_offset = {}
		wordlist = open(wordlist_file)
		for index, word in enumerate(wordlist):
			self.word_offset[word.strip()] = index
		self.size = len(self.word_offset.keys())
		self.keyset = set(self.word_offset.keys())
	def score(self, sentence, tag, word_pos, prev_tag, vector, feature_offset_val, class_offset):
		#print "getting score for:", sentence, tag, word_pos, prev_tag, feature_offset_val, class_offset
		#print "with vector of length:", len(vector)
		word_weight = None
		if sentence[word_pos] not in self.keyset:
			#print "no weights for word:", sentence[word_pos]
			word_weight = 0
		else:
			word_weight = self.word_offset[sentence[word_pos]]
		return vector[class_offset[tag] + feature_offset_val + word_weight]
	
	def update_sentence(self, sentence, tags_star, tags, vector, feature_offset_val, class_offset):
		for index, word in enumerate(sentence):
			if tags_star[index] != tags[index]:
				if word not in self.keyset:
					print "error: word", word, "has no weight"
				else:
					vector[class_offset[tags_star[index]] + feature_offset_val + self.word_offset[word]] -= 1
					vector[class_offset[tags[index]] + feature_offset_val + self.word_offset[word]] += 1
