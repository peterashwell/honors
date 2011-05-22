import psyco
psyco.full()

class acFeature:
	def __init__(self, wordlist, taglist):
		self.id = "ac"
		self.size = 2
		self.class_offset = {}
		for i, tag in enumerate(taglist):
			self.class_offset[tag.strip()] = i * self.size
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0

	def score(self, sentence, tag, word_pos, prev_tag):
		offset = 0
		if len(sentence) == 1:
			return 0
		if word_pos == 0:
			if sentence[1].istitle():
				offset = 1
		elif word_pos == len(sentence) - 1:
			if sentence[-2].istitle():
				offset = 1
		else:
			if sentence[word_pos + 1].istitle() or sentence[word_pos - 1].istitle():
				offset = 1
		return self.weights[self.class_offset[tag] + offset]
	
	def update_sentence(self, sentence, tag_star, tag):
		if len(sentence) == 1:
			return # do nothing
		
		for index, word in enumerate(sentence):
			offset = 0
			if tag_star[index] != tag[index]:
				if index == 0:
					if sentence[index + 1].istitle(): # at start, second word is cap
						offset = 1
				elif index == len(sentence) - 1:
					if sentence[index - 1].istitle(): # at end, second last word is cap
						offset = 1
				else:
					if sentence[index + 1].istitle() or sentence[index - 1].istitle():
						offset = 1
				self.weights[self.class_offset[tag_star[index]] + offset] -= 1
				self.weights[self.class_offset[tag[index]] + offset] += 1
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class icFeature:
	def __init__(self, wordlist, taglist):
		self.id = "ic"
		self.size = 2
		self.class_offset = {}
		for i, tag in enumerate(taglist):
			self.class_offset[tag.strip()] = i * self.size
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0

	def score(self, sentence, tag, word_pos, prev_tag):
		offset = 0
		if sentence[word_pos].istitle():
			offset = 1
		return self.weights[self.class_offset[tag] + offset]
		
	def update_sentence(self, sentence, tag_star, tag):
		for index, word in enumerate(sentence):
			offset = 0
			if tag_star[index] != tag[index]:
				if word.istitle():
					offset = 1
				self.weights[self.class_offset[tag_star[index]] + offset] -= 1
				self.weights[self.class_offset[tag[index]] + offset] += 1
	
	def show_weights(self, vector, class_offset_val, feature_offset_val):
		print "CLASS OFFSET:", class_offset_val
		for word in self.tag_offset.keys():
			print word,'\t',
		print
		for word in self.tag_offset.keys():
			print class_offset_val + self.tag_offset[word] + feature_offset_val, '\t',
		print
		for word in self.tag_offset.keys():
			print vector[class_offset_val + self.tag_offset[word] + feature_offset_val], '\t',
		print
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class pwFeature:
	def __init__(self, wordlist, taglist):
		self.id = "pw"
		self.word_offset = {}
		for index, word in enumerate(wordlist):
			word = word.strip()
			self.word_offset[word] = index
		self.word_offset[''] = index + 1
		
		self.size = len(self.word_offset.keys())
		self.keyset = set(self.word_offset.keys())
		self.class_offset = {}
		for index, tag in enumerate(taglist):
			self.class_offset[tag.strip()] = index * self.size
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0

	def score(self, sentence, tag, word_pos, prev_tag):
		if word_pos == 0:
			prev_word = ''
		else:
			prev_word = sentence[word_pos - 1]
		if prev_word not in self.keyset:
			return 0
		else:
			return self.weights[self.class_offset[tag] + self.word_offset[prev_word]]
	
	def update_sentence(self, sentence, tags_star, tags):
		for index, word in enumerate(sentence):
			if tags_star[index] != tags[index]:
				if index == 0:
					prev_word = ''
				else:
					prev_word = sentence[index - 1]
				self.weights[self.class_offset[tags_star[index]] + self.word_offset[prev_word]] -= 1
				self.weights[self.class_offset[tags[index]] + self.word_offset[prev_word]] += 1
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class nwFeature:
	def __init__(self, wordlist, taglist):
		self.id = "nw"
		self.word_offset = {}
		for index, word in enumerate(wordlist):
			word = word.strip()
			self.word_offset[word] = index
		self.word_offset[''] = index + 1
		
		self.size = len(self.word_offset.keys())
		self.keyset = set(self.word_offset.keys())
		self.class_offset = {}
		for index, tag in enumerate(taglist):
			self.class_offset[tag.strip()] = index * self.size
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0

	def score(self, sentence, tag, word_pos, prev_tag):
		if word_pos == len(sentence) - 1:
			next_word = ''
		else:
			next_word = sentence[word_pos + 1]
		if next_word not in self.keyset:
			return 0
		else:
			return self.weights[self.class_offset[tag] + self.word_offset[next_word]]
	
	def update_sentence(self, sentence, tags_star, tags):
		for index, word in enumerate(sentence):
			if tags_star[index] != tags[index]:
				if index == len(sentence) - 1:
					next_word = ''
				else:
					next_word = sentence[index + 1]
				self.weights[self.class_offset[tags_star[index]] + self.word_offset[next_word]] -= 1
				self.weights[self.class_offset[tags[index]] + self.word_offset[next_word]] += 1
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class ptFeature:
	def __init__(self,wordlist, taglist):
		self.id = "pt"
		self.tag_offset = {}
		self.class_offset = {}

		for index, tag in enumerate(taglist):
			self.tag_offset[tag] = index
		self.tag_offset[''] = index + 1 # NULL tag
		self.size = len(self.tag_offset.keys())
		for index, tag in enumerate(taglist):
			self.class_offset[tag] = index * self.size
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0
		
	def score(self, sentence, tag, word_pos, prev_tag):
		#print "scoring", sentence, tag, word_pos, prev_tag, len(vector), feature_offset_val
		# return score for previous tag for this particular class
		#print self.tag_offset.keys()
		return self.weights[self.class_offset[tag] + self.tag_offset[prev_tag]]
		
	def update_sentence(self, sentence, tag_star, tag):
		for index, word in enumerate(sentence):
			if tag_star[index] != tag[index]:
				if index == 0:
					prev_tag = ''
				else:
					prev_tag = tag_star[index - 1]
				# update incorrect and correct feature vectors
				#print "correcting for tag", tag_star[index], "with", tag[index], "for previous tag >" + prev_tag + "<"
				#print "updating vector position", class_offset[tag_star[index]] + feature_offset_val + self.tag_offset[prev_tag]
				self.weights[self.class_offset[tag_star[index]] + self.tag_offset[prev_tag]] -= 1
				#print "updating vector position", class_offset[tag[index]] + feature_offset_val + self.tag_offset[prev_tag]
				self.weights[self.class_offset[tag[index]] + self.tag_offset[prev_tag]] += 1
	
	def show_weights(self, vector, class_offset_val, feature_offset_val):
		print "CLASS OFFSET:", class_offset_val
		for word in self.tag_offset.keys():
			print word,'\t',
		print
		for word in self.tag_offset.keys():
			print class_offset_val + self.tag_offset[word] + feature_offset_val, '\t',
		print
		for word in self.tag_offset.keys():
			print self.vector[class_offset_val + self.tag_offset[word] + feature_offset_val], '\t',
		print
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class cwFeature:
	def __init__(self, wordlist, taglist):
		self.id = "cw"
		self.word_offset = {}
		for index, word in enumerate(wordlist):
			self.word_offset[word] = index
		self.size = len(self.word_offset.keys())
		self.keyset = set(self.word_offset.keys())
		self.class_offset = {}
		for index, tag in enumerate(taglist):
			self.class_offset[tag.strip()] = index * self.size
		print taglist
		self.weights = [0] * self.size * len(self.class_offset.keys())
		self.weight_sums = [0] * self.size * len(self.class_offset.keys())
		self.rounds = 0

	def score(self, sentence, tag, word_pos, prev_tag):
		#print "getting score for:", sentence, tag, word_pos, prev_tag, feature_offset_val, class_offset
		#print "with vector of length:", len(vector)
		if sentence[word_pos] not in self.keyset:
			#print "no weights for word:", sentence[word_pos]
			return 0
		else:
			return self.weights[self.class_offset[tag] + self.word_offset[sentence[word_pos]]]
	
	def update_sentence(self, sentence, tags_star, tags):
		for index, word in enumerate(sentence):
			if tags_star[index] != tags[index]: # do not match
				if word not in self.keyset:
					print "error: word", word, "has no weight"
				else:
					#print "correcting for tag", tags_star[index], "with", tags[index], "for word", word
					self.weights[self.class_offset[tags_star[index]] + self.word_offset[word]] -= 1
					self.weights[self.class_offset[tags[index]] + self.word_offset[word]] += 1
					#print "updating vector position", class_offset[tags_star[index]] + feature_offset_val + self.word_offset[word]
					#print "updating vector position", class_offset[tags[index]] + feature_offset_val + self.word_offset[word]
	
	def show_weights(self, vector, class_offset_val, feature_offset_val):
		print "CLASS OFFSET:", class_offset_val
		for word in self.word_offset.keys():
			print word,'\t',
		print
		for word in self.word_offset.keys():
			print class_offset_val + self.word_offset[word] + feature_offset_val, '\t',
		print
		for word in self.word_offset.keys():
			print vector[class_offset_val + self.word_offset[word] + feature_offset_val], '\t',
		print
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums
