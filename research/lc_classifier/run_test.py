from classifier import lcClassifier
from dist_funcs import lcss
from utils import crossfold

from os import listdir

clsf = lcClassifier(lcss)
dataset = listdir("lc_data")
N = 5 # nearest neighbors to consider
for test, train in crossfold(10, dataset):
	for test_obj in test:
		true_class = test_obj.strip().split('_')[0]
		clsf.nn_classify(N, test_obj, true_class, train)

