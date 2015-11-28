'''
Train the LDA model from processed data

Python 3.x
'''

import logging, gensim
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary)
id2word = gensim.corpora.Dictionary.load('data/instagram_media.dict')
# load corpus iterator
mm = gensim.corpora.MmCorpus('data/instagram_media.mm')
# start model generation
lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=40, alpha=0.001, eval_every=5, passes=50)
# show the output
lda.print_topics(20)

lda.save('data/lda.model')
