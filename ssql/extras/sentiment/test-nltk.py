from analysis import load_classifier, words_in_tweet, POSITIVE, NEGATIVE, NEUTRAL, word_feats
import collections
import datetime
import nltk

def drange(start, stop, step):
    r = start
    while r <= stop:
        yield r
        r += step

testfile = open('testdata.manual.2009.05.25')

print "Loading classifier"
classifier = load_classifier()

print "Running test"
print "prob, pos prec, pos rec, neg prec, neg rec"
for prob in drange(0.5, 1.0, .01):
    right = 0
    wrong = 0
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)
    testfile.seek(0)
    count = 0
    for line in testfile:
        parts = line.split(";;")
        dist = classifier.prob_classify(word_feats(words_in_tweet(parts[5])))
        if dist.prob(dist.max()) > prob:
            realguess = dist.max()
        else:
            realguess = NEUTRAL
        refsets[parts[0]].add(count)
        testsets[realguess].add(count)
        count += 1
    print "%f, %f, %f, %f, %f" % (prob, nltk.metrics.precision(refsets[POSITIVE], testsets[POSITIVE]), nltk.metrics.recall(refsets[POSITIVE],testsets[POSITIVE]), nltk.metrics.precision(refsets[NEGATIVE], testsets[NEGATIVE]), nltk.metrics.recall(refsets[NEGATIVE], testsets[NEGATIVE]))
