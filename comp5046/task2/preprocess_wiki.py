#!/usr/local/bin/python

# Script to turn json wiki data into feature vectors
# The file has the form:
# num_vectors 
# num_features
# vector_1
# ...
# vector_n
# Each feature vector has the form:
# f1, f2, ... , fn, true_class, article_name
# article_name will be crimped out by the perceptron 

import os
import random
import re

##### Part 0 - Get the correct classifications for each article
correct_class = {}
correct_file = open("wiki_data/correct_class.csv")
for line in correct_file:
	line = line.strip().split(',')
	correct_class[line[0]] = line[1]

##### Part 1 - Build a bag of words feature vector set in ./features
bag_of_words = set() # set containing all word
stop_words_file = open("stop_words.txt")
stop_words = set([obj.strip() for obj in stop_words_file.read().strip().split(',')])

# Some important constants

_REMOVE_PUNCTUATION = True
_REMOVE_STOP_WORDS = True

# Open set of titles for iteration over files
title_file = open("wiki_data/comp5046-titles.txt")
titles = [obj.strip() for obj in title_file.read().strip().split('\n')]

word_index = {} # position of word in feature vector
word_counts = []
article_features = {} # feature vector for article
current_index = 0 # feature index we are up to

# Store each count for a word w in article a in article_features[a][word_position[w]]
for title in titles:
	article_fname = "wiki_data/comp5046-articles/" + title + ".txt"
	article_text = open(article_fname)
	print "reading:", article_fname

	article_features[title] = [0] * len(bag_of_words) # have at least as many indices as last run
	for line in article_text:
		words = line.strip().split(' ')
		words = [re.sub("[\"'-]", '', word) for word in words] # eliminate quotes, hyphens etc
		if _REMOVE_PUNCTUATION: # filter out any punctuation, including
			words = filter(lambda word: re.match("\w+", word), words)
		if _REMOVE_STOP_WORDS: # filter out stop words
			words = filter(lambda word: word not in stop_words, words)
		for word in words:
			if word in bag_of_words:
				article_features[title][word_index[word]] += 1
				word_counts[word_index[word]] += 1
			else:
				bag_of_words.add(word)
				word_index[word] = current_index
				current_index += 1
				article_features[title].append(1)
				word_counts.append(1)
	article_text.close()
print len(bag_of_words), "words in bag"

# Write out bag of word feature set in ./features/bag_of_words
bow_out = open("features/bag_of_words.csv", 'w')
num_features = len(bag_of_words)
for title in sorted(article_features.keys()):
	first = True
	print "writing", title
	features = article_features[title]
	features = features + [0] * (num_features - len(features)) # pad with 0s
	features += [correct_class[title], title]
	for index in xrange(len(features)):
		if features[index] == 0: 
			continue # sparse
		if not first:
			bow_out.write(',')
		first = False
		if num_features - index <= 2:
			bow_out.write(str(features[index]))
			first = False
		else:
			bow_out.write(str(index) + "_" + str(features[index]))
			first = False
	bow_out.write('\n')
bow_out.close()

# TODO normalise this cunt

