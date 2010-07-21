from analysis import save_classifier, words_in_tweet, POSITIVE, NEGATIVE, NEUTRAL
from nltk.metrics.association import BigramAssocMeasures

import collections, itertools
import datetime
import nltk
import nltk.classify.util, nltk.metrics
import os
import pickle
import re


# lots of stuff from http://streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/
# and http://nltk.googlecode.com/svn/trunk/doc/book/ch06.html

#smilefile = open('smiley.txt.processed.2009.05.25')
#frownfile = open('frowny.txt.processed.2009.05.25')
smilefile = open('happy.txt')
frownfile = open('sad.txt')

def features(feat_func, handle, label):
    print "Generating features for '%s'" % (label)
    print datetime.datetime.now()
    return [((feat_func(words_in_tweet(line))), label) for line in handle]

def update_wordcount(word_fd, label_word_fd, handle, label):
    print "Counting '%s'" % (label)
    print datetime.datetime.now()
    for line in handle:
        for word in words_in_tweet(line):
            word_fd.inc(word)
            label_word_fd[label].inc(word)
    handle.seek(0)

word_fd = nltk.probability.FreqDist()
label_word_fd = nltk.probability.ConditionalFreqDist()
update_wordcount(word_fd, label_word_fd, smilefile, POSITIVE)
update_wordcount(word_fd, label_word_fd, frownfile, NEGATIVE)

pos_word_count = label_word_fd[POSITIVE].N()
neg_word_count = label_word_fd[POSITIVE].N()
total_word_count = pos_word_count + neg_word_count

print "Finding top words"
word_scores = {}
for word, freq in word_fd.iteritems():
    pos_score = BigramAssocMeasures.chi_sq(label_word_fd[POSITIVE][word],
        (freq, pos_word_count), total_word_count)
    neg_score = BigramAssocMeasures.chi_sq(label_word_fd[NEGATIVE][word],
        (freq, neg_word_count), total_word_count)
    word_scores[word] = pos_score + neg_score

best = sorted(word_scores.iteritems(), key=lambda (w,s): s, reverse=True)[:10000]
bestwords = set([w for w, s in best])
print "Best words"
#print bestwords
def best_word_feats(words):
    return dict([(word, True) for word in words if word in bestwords])

posfeats = features(best_word_feats, smilefile, POSITIVE)
negfeats = features(best_word_feats, frownfile, NEGATIVE)
classifier = nltk.NaiveBayesClassifier.train(posfeats + negfeats)
save_classifier(classifier)
