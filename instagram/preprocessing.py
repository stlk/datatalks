'''
This script:

* Loads text data from the database
* Cleans them up
* Creates a dictionary and corpus that can be used to train an LDA model
* Training of the LDA model is not included but follows:
  lda = models.LdaModel(corpus, id2word=dictionary, num_topics=100, passes=100)

Author: Alex Perrier
Python 3.x
'''

import langid
import nltk
import re
import time
from collections import defaultdict
from gensim import corpora, models, similarities
from nltk.tokenize import RegexpTokenizer
import psycopg2
import psycopg2.extras
from string import digits

import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

conn = psycopg2.connect("dbname=instagram_lda user=pc")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

cur.execute("SELECT * FROM media")
tweets = cur.fetchall()

# Load data from db
# Filter out timelines with less than 2 tweets
documents    = [tw['raw_text'] for tw in tweets
                    if ('n_media' in tw.keys()) and (tw['n_media'] > 2)]

print("We have " + str(len(documents)) + " records")

# Remove urls
documents = [re.sub(r"(?:\@|http?\://)\S+", "", doc)
                for doc in documents ]

# Remove documents with less 100 words (some timeline are only composed of URLs)
documents = [doc for doc in documents if len(doc) > 20]

# tokenize
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')
documents = [ tokenizer.tokenize(doc.lower()) for doc in documents ]

# Remove stop words
stoplist_tw=['amp','get','got','hey','hmm','hoo','hop','iep','let','ooo','par',
            'pdt','pln','pst','wha','yep','yer','aest','didn','nzdt','via',
            'one','com','new','like','great','make','top','awesome','best',
            'good','wow','yes','say','yay','would','thanks','thank','going',
            'new','use','should','could','best','really','see','want','nice',
            'while','know']

unigrams = [ w for doc in documents for w in doc if len(w)==1]
bigrams  = [ w for doc in documents for w in doc if len(w)==2]

stoplist  = set(nltk.corpus.stopwords.words("english") + stoplist_tw
                + unigrams + bigrams)
documents = [[token for token in doc if token not in stoplist]
                for doc in documents]

# rm numbers only words
documents = [ [token for token in doc if len(token.strip(digits)) == len(token)]
                for doc in documents ]

# Lammetization
# This did not add coherence ot the model and obfuscates interpretability of the
# Topics. It was not used in the final model.
#   from nltk.stem import WordNetLemmatizer
#   lmtzr = WordNetLemmatizer()
#   documents=[[lmtzr.lemmatize(token) for token in doc ] for doc in documents]

# Remove words that only occur once
token_frequency = defaultdict(int)

# count all token
for doc in documents:
    for token in doc:
        token_frequency[token] += 1

# keep words that occur more than once
documents = [ [token for token in doc if token_frequency[token] > 1]
                for doc in documents  ]

# Sort words in documents
for doc in documents:
    doc.sort()

# Build a dictionary where for each record each word has its own id
dictionary = corpora.Dictionary(documents)
dictionary.compactify()
# and save the dictionary for future use
dictionary.save('data/instagram_media.dict')

# We now have a dictionary with x unique tokens
print(dictionary)

# Build the corpus: vectors with occurence of each word for each document
# convert tokenized documents to vectors
corpus = [dictionary.doc2bow(doc) for doc in documents]

# and save in Market Matrix format
corpora.MmCorpus.serialize('data/instagram_media.mm', corpus)
# this corpus can be loaded with corpus = corpora.MmCorpus('filename.mm')
