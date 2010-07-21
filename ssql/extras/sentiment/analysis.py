from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews, stopwords
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.probability import FreqDist, ConditionalFreqDist

import gzip
import os
import pickle
import re
import nltk

POSITIVE = "4"
NEGATIVE = "0"
NEUTRAL = "2"

mention_re = re.compile(ur"\@\S+", re.UNICODE)
url_re = re.compile(ur"((mailto\:|(news|(ht|f)tp(s?))\://){1}\S+)", re.UNICODE)
emoticon_re = re.compile(ur"\:\)|\:\-\)|\: \)|\:D|\=\)|\:\(\:\-\(\: \(", re.UNICODE)
tokenizer = nltk.RegexpTokenizer(r'\w+')

def word_feats(words):
    return dict([(word, True) for word in words])

def words_in_tweet(inputstr):
    outputstr = inputstr
    outputstr = mention_re.sub("MENTION_TOKEN", outputstr)
    outputstr = url_re.sub("URL_TOKEN", outputstr)
    outputstr = emoticon_re.sub("", outputstr)
    outputstr = outputstr.lower()
    return tokenizer.tokenize(outputstr)

# from http://groups.google.com/group/nltk-users/browse_thread/thread/be28ed12f87384ea
# Save Classifier 
def save_classifier(classifier): 
    fModel = open('BayesModel.pkl',"wb") 
    pickle.dump(classifier, fModel,1) 
    fModel.close() 
    os.system("rm BayesModel.pkl.gz") 
    os.system("gzip BayesModel.pkl") 
# Load Classifier
def load_classifier(): 
    os.system("gunzip BayesModel.pkl.gz") 
    fModel = open('BayesModel.pkl',"rb") 
    classifier = pickle.load(fModel) 
    fModel.close() 
    os.system("gzip BayesModel.pkl") 
    return classifier
# Package classifier for actual use
def package_classifier(to_pickle):
    fp = gzip.open('sentiment.pkl.gz', 'wb')
    pickle.dump(to_pickle, fp, 1)
    fp.close()
