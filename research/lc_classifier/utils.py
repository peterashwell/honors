def crossfold(folds, dataset):
	fold_size = len(dataset) / folds
	fold_left = len(dataset) % folds
	print "fold size:", fold_size
	print "fold left:", fold_left
	# For each fold yield fold number and section of dataset
	prev_end = None # keep track of last endpoint for fold
	for fold_num in xrange(folds):
		if fold_left > 0:
			offset = 1
			fold_left -= 1
		else:
			offset = 0
		if prev_end is None: # first run
			fold_start = 0
			fold_end = 0 + fold_size + offset
			prev_end = fold_end
		else:
			fold_start = prev_end
			fold_end = fold_start + fold_size + offset
			prev_end = fold_end # record last endpoint
		
		test = dataset[fold_start : fold_end]
		train = dataset[:fold_start] + dataset[fold_end:]
		yield test, train
