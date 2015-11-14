'''
Load the corpus and dictionary

Python 2.7
'''

from gensim import corpora, models
import pyLDAvis.gensim

corpus = corpora.MmCorpus('data/instagram_media.mm')
dictionary = corpora.Dictionary.load('data/instagram_media.dict')

lda = models.LdaModel.load('data/lda.model')
data =  pyLDAvis.gensim.prepare(lda, corpus, dictionary)
pyLDAvis.display(data)
