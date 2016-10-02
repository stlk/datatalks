# Load the corpus and dictionary
from gensim import corpora, models
import pyLDAvis.gensim

corpus = corpora.MmCorpus('data/twitter.mm')
dictionary = corpora.Dictionary.load('data/twitter.dict')

# First LDA model with 10 topics, 10 passes, alpha = 0.001
lda = models.LdaModel.load('data/lda.model')
followers_data =  pyLDAvis.gensim.prepare(lda, corpus, dictionary)
# pyLDAvis.display(followers_data)
