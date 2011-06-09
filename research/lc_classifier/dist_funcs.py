from math import sqrt
from math import fabs
from utils import linearapprox

# Euclidean distance between two light curves
def euclidean(lc_a, lc_b):
	return None

# Simple temporal grammar with linear approximations

def simplegrammar(lc_a, lc_b):
	#Not using these yet...
	#INDEL_PENALTY = 1.5
	#MATCH_PENALTY = 1

	# Build linear approximations
	approx_a = linearapprox(lc_a, 3)
	approx_b = linearapprox(lc_b, 3)
	
	m = len(approx_a)
	n = len(approx_b)	
	# Compute edit distance
	# Half penalties for continued regions, harsh penalties for sudden changes in gradient
	backtrace = [['-'] * n for i in xrange(m)]
	scores = [[0] * n for i in xrange(m)]
	
	for i in xrange(m):
		for j in xrange(n):
			if j == 0 and i == 0:
				#print approx_a[i]
				scores[i][j] = fabs(approx_a[i][2] - approx_b[j][2])
			elif i == 0:
				scores[i][j] = scores[i][j - 1] + fabs(approx_a[i][2] - approx_b[j][2])
				backtrace[i][j] = 'l'
			elif j == 0:
				scores[i][j] = scores[i - 1][j] + fabs(approx_a[i][2] - approx_b[j][2])
				backtrace[i][j] = 'u'
			else:
				best_direction = 'd'
				best_score = scores[i - 1][j - 1]
				if scores[i - 1][j] < best_score:
					best_direction = 'u'
					best_score = scores[i - 1][j]
				elif scores[i][j - 1] < best_score:
					best_direction = 'l'
					best_score = scores[i][j - 1]
				scores[i][j] = best_score + fabs(approx_a[i][2] - approx_b[j][2])
				backtrace[i][j] = best_direction
	return scores[m - 1][n - 1]


# Dynamic time warping distance between two light curves
def dtw(lc_a, lc_b):
	# Ignore time dimension in DTW (for now)
	lc_a = lc_a[1]
	lc_b = lc_b[1] 
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
						pass
						#print scores[i - 1][j]
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
#	print '\t' + '\t'.join(str(obj) for obj in lc_b)
#	print '\n'.join('\t'.join([str(lc_a[i])] + [str(obj) for obj in row]) for i, row in enumerate(backtrace))
#	print
#	print '\t' + '\t'.join(str(obj) for obj in lc_b)
#	print '\n'.join('\t'.join([str(lc_a[i])] + [str(obj) for obj in row]) for i, row in enumerate(scores))
#	print scores[m - 1][n - 1]
	return scores[m - 1][n - 1]
