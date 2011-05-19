import psyco
psyco.full()

def viterbi(sentence, global_tags, vector, class_offset, featureset):	
	score_matrix = [['-'] * len(global_tags) for i in xrange(len(sentence))]
	backpointers = [['-'] * len(global_tags) for i in xrange(len(sentence))]
	first_word = True
	for row, word in enumerate(sentence):
		for col, tag in enumerate(global_tags):
			#print "vitrowcol:", row, col, tag
			if first_word: # if on the first word, just fill out the row
				prev_tag = ''
				score_matrix[row][col] = featureset.tag_score(sentence, tag, row, prev_tag, vector, class_offset)
				#print "updating", row, col
			else:
				best_prev_tag = None
				best_score = None
				for prev_tag_col, prev_tag in enumerate(global_tags): # for each previous tag
					#print "transitioning from", prev_tag, "to", tag
					#print "best score:", best_score
					if best_prev_tag is None:
						#print "prev tag:", global_tags[prev_tag_col], "score is", score_matrix[row - 1][prev_tag_col]
						print score_matrix[row - 1][prev_tag_col]
						best_score = featureset.tag_score(sentence, tag, row, prev_tag, vector, class_offset) + score_matrix[row - 1][prev_tag_col]
						best_prev_tag = prev_tag_col
					else:
						new_score = featureset.tag_score(sentence, tag, row, prev_tag, vector, class_offset) + score_matrix[row - 1][prev_tag_col]
						if new_score > best_score:
							best_score = new_score
							#print "found better score:", best_score, "for tag:", global_tags[prev_tag_col]
							best_prev_tag = prev_tag_col
				#print "setting sm", row, col, "to", best_score
				score_matrix[row][col] = best_score
				backpointers[row][col] = best_prev_tag
				#print "sm row:", row, score_matrix[row]
		#print "viterbi array:"
		#print score_matrix
		first_word = False

	# Now get the optimal tag list out
	optimal_tags = []
	first_bp = True
	backpointer = None
	print "backpointers:" 
	print '\n'.join(['\t'.join([str(el) for el in obj]) for obj in backpointers])
	print "sm:"
	print '\n'.join(['\t'.join([str(el) for el in obj]) for obj in score_matrix])
	
	for row in reversed(xrange(len(sentence))):
		if first_bp:
			first_tag = True
			best_tag = None
			best_score = None
			for col, tag in enumerate(global_tags):
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
		if row == 0: # account for single word sentence
			continue
		backpointer = backpointers[row][backpointer]
		optimal_tags = [best_tag] + optimal_tags # builds in correct order
	return optimal_tags	
