from utils import crossfold
dataset = range(55)

for test, train in crossfold(10, dataset):
	print test, train
