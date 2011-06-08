from math import sqrt
from math import fabs

# Euclidean distance between two light curves
def euclidean(lc_a, lc_b):
	return None

# Dynamic time warping distance between two light curves
def dtw(lc_a, lc_b):
	# Create len(lc_b) x len(lc_a) matrix for backpointers and scores
	m = len(lc_a)
	n = len(lc_b)
	backtrace = [['-'] * n for i in xrange(m)]
	scores = [[0] * n for i in xrange(m)]
	
	scores[m - 1][n - 1] = fabs(lc_a[m - 1] - lc_b[n - 1])
	
	# Fill out score matrix and compute backpointers
	for i in xrange(m):
		for j in xrange(n):
			if j == 0 and i == 0: # Just fill out
				scores[i][j] = fabs(lc_a[i] - lc_b[j])
			else:
				current_dist = fabs(lc_a[i] - lc_b[j])
				if i == 0: # First row
					scores[i][j] = scores[i][j - 1] + current_dist
					backtrace[i][j] = 'l'
				elif j == 0: # First column
					if j == 0 and i == 2:
						print scores[i - 1][j]
					scores[i][j] = scores[i - 1][j] + current_dist
					backtrace[i][j] = 'u'
				else: # Else, compute best transition score
					best_transition = 'd'
					best_score = scores[i - 1][j - 1]
					if scores[i - 1][j] < best_score:
						best_transition = 'u'
						best_score = scores[i - 1][j]
					if scores[i][j - 1] < best_score:
						best_transition = 'l'
						best_score = scores[i][j - 1]
					scores[i][j] = best_score + current_dist
					backtrace[i][j] = best_transition
	
	# Simply return final score value
	print '\t' + '\t'.join(str(obj) for obj in lc_b)
	print '\n'.join('\t'.join([str(lc_a[i])] + [str(obj) for obj in row]) for i, row in enumerate(backtrace))
	print
	print '\t' + '\t'.join(str(obj) for obj in lc_b)
	print '\n'.join('\t'.join([str(lc_a[i])] + [str(obj) for obj in row]) for i, row in enumerate(scores))
	print scores[m - 1][n - 1]
	return scores[m - 1][n - 1]
