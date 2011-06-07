import psyco
psyco.full()

class NERFeature:
	def __init__(self, wordlist, taglist, size):
		self.weights = [0] * self.size * len(taglist) # weights
		self.weight_sums = [0] * self.size * len(taglist) # for averaging
		self.class_offset = {}
		for i, tag_class in enumerate(taglist): # build tag partitions
			self.class_offset[tag_class.strip()] = i * self.size
		self.rounds = 0
	
	def finish_round(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] += self.weights[i]
		self.rounds += 1	

	def finish_training(self):
		for i in xrange(len(self.weight_sums)):
			self.weight_sums[i] /= (self.rounds * 1.0)
		self.weights = self.weight_sums

class prefFeature(NERFeature):
	def __init__(self, preflist, taglist, pos):
		self.id = 'pref'
		self.pref_offset = {}
		for i, pref in enumerate(preflist):
			self.pref_offset[pref] = i
		self.size = len(self.pref_offset.keys())
		NERFeature.__init__(self, [], taglist, self.size)
		self.keyset = set(self.pref_offset.keys())
		self.position = pos

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		pref_word_pos = word_pos + self.position
		if pref_word_pos < 0 or pref_word_pos >= len(sentence):
			return 0

		pref = sentence[pref_word_pos]
		if len(pref) < 3:
			return 0
		pref = pref[:3].lower()
		if pref not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.pref_offset[pref]]

	def update_sentence(self, sentence, poslist, tags_star, tags):
		for index in xrange(len(sentence)):
			tag_star = tags_star[index]
			tag = tags[index]
			if tag != tag_star:
				pref_word_pos = index + self.position
				if pref_word_pos < 0 or pref_word_pos >= len(sentence):
					return
				pref = sentence[pref_word_pos][:3].lower()
				if len(pref) > 2:
					if pref in self.keyset:
						return self.weights[self.class_offset[tag] + self.pref_offset[pref]]

class suffFeature(NERFeature):
	def __init__(self, sufflist, taglist, pos):
		self.id = 'suff'
		self.suff_offset = {}
		for i, suff in enumerate(sufflist):
			self.suff_offset[suff.lower()] = i
		self.size = len(self.suff_offset.keys())
		NERFeature.__init__(self, [], taglist, self.size)
		self.keyset = set(self.suff_offset.keys())
		self.position = pos

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		suff_word_pos = word_pos + self.position
		if suff_word_pos < 0 or suff_word_pos >= len(sentence):
			return 0

		suff = sentence[suff_word_pos]
		if len(suff) < 3:
			return 0
		suff = suff[-3:].lower()
		if suff not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.suff_offset[suff]]

	def update_sentence(self, sentence, poslist, tags_star, tags):
		for index in xrange(len(sentence)):
			tag_star = tags_star[index]
			tag = tags[index]
			if tag != tag_star:
				suff_word_pos = index + self.position
				if suff_word_pos < 0 or suff_word_pos >= len(sentence):
					return
				suff = sentence[suff_word_pos][-3:].lower()
				if len(suff) > 2:
					if suff in self.keyset:
						return self.weights[self.class_offset[tag] + self.suff_offset[suff]]

class hypFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "hyp"
		self.size = 1
		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		if '-' not in sentence[word_pos]:
			return 0
		else:
			return self.weights[self.class_offset[tag]]
	
	def update_sentence(self, sentence, poslist, tags_star, tags):
		for index in xrange(len(sentence)):
			tag = tags[index]
			tag_star = tags_star[index]
			if tag != tag_star:
				if '-' in sentence[index]:
					self.weights[self.class_offset[tag]] += 1
					self.weights[self.class_offset[tag_star]] -= 1

class horgFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "horg"
		self.size = 1
		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		# if league, inc, corp, co, ltd, team group, consolidated, committee appears nearby
		for search_pos in xrange(max(0, word_pos - 4), \
				min(len(sentence), word_pos + 4)):
			for org_word in ["inc", "co", "ltd", \
								"team", "group", "consolidated" \
								"committee", "league"]:
				if sentence[word_pos].lower().find(org_word) != -1:
					return self.weights[self.class_offset[tag]]
		return 0
	
	def update_sentence(self, sentence, poslist,tags_star, tags):
		for index in xrange(len(sentence)):
			tag_star = tags_star[index]
			tag = tags[index]
			if tag != tags_star:
				for search_pos in xrange(max(0, index - 4), \
						min(len(sentence), index + 4)):
					for org_word in ["inc", "co", "ltd", \
								"team", "group", "consolidated" \
								"committee", "league", "community"]:
						if sentence[index].lower().find(org_word) != -1:
							self.weights[self.class_offset[tag]] += 1
							self.weights[self.class_offset[tag_star]] -= 1
								

class hnFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "hn"
		self.size = 1
		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		num_numeric = 0
		for word in sentence:
			if word.isdigit():
				num_numeric += 1
		if num_numeric > (len(sentence) * 0.3): # greater than 30% numbers
			return self.weights[self.class_offset[tag]]
		return 0
	
	def update_sentence(self, sentence, poslist,tags_star, tags):
		num_numeric = 0
		for word in sentence:
			if word.isdigit():
				num_numeric += 1
		if num_numeric < (len(sentence) * 0.3):
			return
		for index in xrange(len(sentence)):
			tag_star = tags_star[index]
			tag = tags[index]
			if tag != tag_star:
				self.weights[self.class_offset[tag]] += 1
				self.weights[self.class_offset[tag_star]] -= 1

class brFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "br"
		self.size = 1
		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist,  word_pos, prev_tag):
		search_pos = word_pos - 1
		has_lbrack = False
		has_rbrack = False
		while search_pos >= 0 and word_pos - search_pos < 3: # within 2 words 
			if sentence[search_pos] == '(':
				has_lbrack = True
				break
			search_pos -= 1
		search_pos = word_pos + 1
		while search_pos < len(sentence) and search_pos - word_pos < 3:
			if sentence[search_pos] == '(':
				has_rbrack = True
				break
			search_pos += 1
		if has_lbrack and has_rbrack:
			return self.weights[self.class_offset[tag]]
		return 0

	def update_sentence(self, sentence, poslist,tags_star, tags):
		for index in xrange(len(sentence)):
			tag_star = tags_star[index]
			tag = tags[index]
			if tag != tag_star:
				has_lbrack = False
				has_rbrack = False
				search_pos = index - 1
				while search_pos >= 0 and index - search_pos < 3: # within 2 words 
					if sentence[search_pos] == '(':
						has_lbrack = True
						break
					search_pos -= 1
				search_pos = index + 1
				while search_pos < len(sentence) and search_pos - index < 3:
					if sentence[search_pos] == '(':
						has_rbrack = True
						break
					search_pos += 1
				if has_lbrack and has_rbrack:
					self.weights[self.class_offset[tag]] += 1
					self.weights[self.class_offset[tag_star]] -= 1

class allcFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = 'allc'
		self.size = 1
		NERFeature.__init__(self, wordlist, taglist, self.size)

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		if not sentence[word_pos].isupper():
			return 0
		else:
			for word in sentence: # not every word capitalised
				if word.isalpha():
					if not word.isupper(): 
						return self.weights[self.class_offset[tag]]
		return 0
	
	def update_sentence(self, sentence, poslist, tags_star, tags):
		allcaps = True
		for word in sentence:
			if word.isalpha():
				if not word.isupper():
					allcaps = False
					break
		if allcaps:
			return
		for i in xrange(len(tags)):
			tag_star = tags_star[i]
			tag = tags[i]
			if tag_star != tag:
				self.weights[self.class_offset[tag]] += 1
				self.weights[self.class_offset[tag_star]] -= 1

class facFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = 'fac'
		self.word_offsets = {}
		for i, word in enumerate(wordlist): # build word score list
			self.word_offsets[word.lower()] = i
		self.keyset = set(self.word_offsets.keys())
		self.size = len(self.word_offsets.keys())

		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist,  word_pos, prev_tag):
		if not sentence[word_pos].istitle():
			return 0
		index = word_pos
		nntw = None # next non-title word
		word = sentence[index]
		while word.istitle():
			word = sentence[index]
			index += 1
			if index == len(sentence):
				return 0
		nntw = word
		if nntw not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.word_offsets[nntw.lower()]]
	
	def update_sentence(self, sentence, poslist,tags_star, tags):
		for word_num in xrange(len(tags)):
			tag_star = tags_star[word_num]
			tag = tags[word_num]
			if tag_star != tag: # incorrect tagging
				nntw = None
				search_point = word_num
				nntw = None
				search_word = sentence[search_point]
				while search_word.istitle():
					search_word = sentence[search_point]
					search_point += 1
					if search_point == len(sentence):
						return
				nntw = search_word
				self.weights[self.class_offset[tag] + self.word_offsets[nntw.lower()]] += 1
				self.weights[self.class_offset[tag_star] + self.word_offsets[nntw.lower()]] -= 1 

class fbcFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = 'fbc'
		self.word_offsets = {}
		for i, word in enumerate(wordlist): # build word score list
			self.word_offsets[word.lower()] = i
		self.size = len(self.word_offsets.keys())
		self.keyset = set(self.word_offsets.keys())
		NERFeature.__init__(self, wordlist, taglist, self.size)
	
	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		if not sentence[word_pos].istitle():
			return 0
		index = word_pos
		nntw = None # previous non-title word
		word = sentence[index]
		while word.istitle():
			word = sentence[index]
			index -= 1
			if index == -1:
				return 0
		nntw = word
		if nntw not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.word_offsets[nntw.lower()]]
	
	def update_sentence(self, sentence, poslist, tags_star, tags):
		for word_num in xrange(len(tags)):
			tag_star = tags_star[word_num]
			tag = tags[word_num]
			if tag_star != tag: # incorrect tagging
				nntw = None
				search_point = word_num
				nntw = None
				search_word = sentence[search_point]
				while search_word.istitle():
					search_word = sentence[search_point]
					search_point -= 1
					if search_point == -1:
						return
				nntw = search_word
				self.weights[self.class_offset[tag] + self.word_offsets[nntw.lower()]] += 1
				self.weights[self.class_offset[tag_star] + self.word_offsets[nntw.lower()]] -= 1 

class acFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "ac"
		self.size = 2
		NERFeature.__init__(self, wordlist, taglist, self.size)

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
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
	
	def update_sentence(self, sentence, poslist, tag_star, tag):
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

class icFeature(NERFeature):
	def __init__(self, wordlist, taglist):
		self.id = "ic"
		self.size = 2
		NERFeature.__init__(self, wordlist, taglist, self.size)

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		offset = 0
		if sentence[word_pos].istitle():
			offset = 1
		return self.weights[self.class_offset[tag] + offset]
		
	def update_sentence(self, sentence, poslist, tag_star, tag):
		for index, word in enumerate(sentence):
			offset = 0 # update for not capitalised
			if tag_star[index] != tag[index]:
				if word.istitle():
					offset = 1
				self.weights[self.class_offset[tag_star[index]] + offset] -= 1
				self.weights[self.class_offset[tag[index]] + offset] += 1

class ptFeature(NERFeature):
	def __init__(self,wordlist, taglist):
		self.id = "pt"
		self.tag_offset = {}
		self.class_offset = {}
		for index, tag in enumerate(taglist):
			self.tag_offset[tag] = index
		self.tag_offset[''] = index + 1 # NULL tag
		self.size = len(self.tag_offset.keys())
		NERFeature.__init__(self, wordlist, taglist, self.size)
			
	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		return self.weights[self.class_offset[tag] + self.tag_offset[prev_tag]]
		
	def update_sentence(self, sentence, poslist, tag_star, tag):
		for index, word in enumerate(sentence):
			if tag_star[index] != tag[index]:
				if index == 0:
					prev_tag = ''
				else:
					prev_tag = tag_star[index - 1]
				self.weights[self.class_offset[tag_star[index]] + self.tag_offset[prev_tag]] -= 1
				self.weights[self.class_offset[tag[index]] + self.tag_offset[prev_tag]] += 1

class wpFeature(NERFeature):
	def __init__(self, wordlist, taglist, wp):
		self.id = "wp" + str(wp)
		self.word_offset = {}
		for index, word in enumerate(wordlist):
			self.word_offset[word.lower()] = index
		if wp != 0:
			self.word_offset[''] = index + 1 # for ends and starts of sentences	
		self.keyset = set(self.word_offset.keys())
		self.size = len(self.word_offset.keys())
		self.word_position = wp
		NERFeature.__init__(self, wordlist, taglist, self.size)

	def score(self, sentence, tag, poslist, word_pos, prev_tag):
		word_pos += self.word_position
		word = None
		if word_pos < 0 or word_pos >= len(sentence):
			word = ''
		else:
			word = sentence[word_pos].lower()
		if word not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.word_offset[word]]
	
	def update_sentence(self, sentence, poslist, tags_star, tags):
		for index in xrange(len(sentence)):
			if tags_star[index] != tags[index]: # do not match
				word_pos = index + self.word_position
				if word_pos < 0 or word_pos >= len(sentence):
					word = ''
				else:
					word = sentence[word_pos].lower()
				self.weights[self.class_offset[tags_star[index]] + self.word_offset[word]] -= 1
				self.weights[self.class_offset[tags[index]] + self.word_offset[word]] += 1

class ppFeature(NERFeature):
	def __init__(self, wordlist, taglist, poslist, posp):
		self.id = "pp" + str(posp)
		self.pos_offset = {}
		for index, pos in enumerate(poslist):
			self.pos_offset[pos] = index
		self.keyset = set(self.pos_offset.keys())
		self.size = len(self.keyset)
		self.pos_position = posp
		NERFeature.__init__(self, wordlist, taglist, self.size)
		
	def score(self, sentence, poslist, tag, word_pos, prev_tag):
		word_pos += self.pos_position
		pos = None
		if word_pos < 0 or word_pos >= len(poslist):
			return 0
		else:
			pos = poslist[word_pos]
		if pos not in self.keyset:
			return 0
		return self.weights[self.class_offset[tag] + self.pos_offset[pos]]	
	
	def update_sentence(self, sentence, poslist, tags_star, tags):
		for index in xrange(len(sentence)):
			if tags_star[index] != tags[index]: # do not match
				index += self.pos_position
				pos = None
				if index < 0 or index >= len(poslist):
					return # do nothing at start of sentence or end
				else:
					pos = poslist[index]
				self.weights[self.class_offset[tags_star[index]] + self.pos_offset[pos]] -= 1
				self.weights[self.class_offset[tags[index]] + self.pos_offset[pos]] += 1
