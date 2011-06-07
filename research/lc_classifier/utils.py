def crossfold(folds, dataset):
	fold_size = len(dataset) / folds
	fold_left = len(dataset) % folds
	print "fold size:", fold_size
	# For each fold yield fold number and section of dataset
	for fold_num in xrange(folds):
		if fold_left > 0:
			offset = 1
		else:
			offset = 0
		fold_start = fold_num * fold_size + offset
		fold_end = fold_start + fold_size

		yield fold_num, dataset[fold_start : fold_end]
