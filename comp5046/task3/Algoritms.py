def viterbi(sentence, tags, vector, class_offset, featureset):
	score_matrix = [[] * len(tags)] * len(sentence)
	backpointers = [[] * len(tags)] * len(sentence)
	first_word = True
	for row, word in enumerate(sentence):
		for col, tag in enumerate(tags):
			if first_word:
				prev_tag = ''
				score_matrix[row][col] = featureset.tag_score(sentence, tag, row, prev_tag, vector)
			else:
				best_prev_tag = None
				best_score = None
				for tag_col, tag in enumerate(tags):
					if best_prev_tag is None:
						best_score = featureset.tag_score(sentence, tag, row, tags[tag_col], vector) + score_matrix[row][tag_col]
						best_prev_tag = tag_col
					else:
						new_score = featureset.tag_score(sentence, tag, row, tags[tag_col], vector) + score_matrix[row][tag_col]
						if new_score > best_score:
							best_prev_tag = tag_col
				score_matrix[row][col] = best_score
				backpointers[row][col] = tag_col
		first_word = False
	
	# Now get the optimal tag list out
	optimal_tags = []
	first_bp = True
	backpointer = None
	for row in reversed(xrange(len(sentence))):
		if first_bp:
			first_tag = True
			best_tag = None
			best_score = None
			for col, tag in enumerate(tags):
				if first_tag is True:
					first_tag = False
					best_tag = tag
					best_score = score_matrix[row][col]
					backpointer = backpointers[row][col]
				else:
					if score_matrix[row][col] > best_score:
						best_tag = tag
						backpointer = backpointers[row][col]
			optimal_tags.append(best_tag)
			first_bp = False
		# Now find the backpointers across the whole way
		backpointer = backpointers[row][backpointer]
		optimal_tags = [best_tag] + optimal_tags # builds in correct order
	
	return optimal_tags	
