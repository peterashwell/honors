import psyco
import math
psyco.full()

def greedy(sentence, global_tags, featureset):
	prev_tag = ''
	tags_star = []
	for word_pos in xrange(len(sentence)):
		best_tag = None
		best_score = None
		for tag in global_tags:
			if best_tag is None:
				best_score = featureset.tag_score(sentence, tag, word_pos, prev_tag)
				best_tag = tag
			else:
				new_score = featureset.tag_score(sentence, tag, word_pos, prev_tag)
				if new_score > best_score:
					best_score = new_score
					best_tag = tag
		tags_star.append(best_tag)
		prev_tag = best_tag
	return tags_star
				
def viterbi(sentence, global_tags, featureset):	
	score_matrix = [[-1] * len(global_tags) for i in xrange(len(sentence))]
	backpointers = [[-1] * len(global_tags) for i in xrange(len(sentence))]
	
	prev_tag = ''
	for col, tag in enumerate(global_tags):
		score_matrix[0][col] = featureset.tag_score(sentence, tag, 0, prev_tag)
	
	for row, word in enumerate(sentence):
		for col, tag in enumerate(global_tags):
			best_prev_tag = None
			best_score = None
			for prev_tag_col, prev_tag in enumerate(global_tags): # for each previous tag
				if best_prev_tag is None:
					best_score = featureset.tag_score(sentence, tag, row, prev_tag) + score_matrix[row - 1][prev_tag_col]
					best_prev_tag = prev_tag_col
				else:
					new_score = featureset.tag_score(sentence, tag, row, prev_tag) + score_matrix[row - 1][prev_tag_col]
					if new_score > best_score:
						best_score = new_score
						best_prev_tag = prev_tag_col
			score_matrix[row][col] = best_score
			backpointers[row][col] = best_prev_tag

	backpointer = score_matrix[-1].index(max(score_matrix[-1]))
	optimal_tags = [global_tags[backpointer]] # add first element
	for row in reversed(xrange(1, len(sentence))):
		backpointer = backpointers[row][backpointer]
		optimal_tags.append(global_tags[backpointer])
	
	optimal_tags.reverse()
	return optimal_tags	
