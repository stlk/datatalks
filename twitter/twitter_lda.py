import logging, gensim, bz2
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = gensim.corpora.Dictionary.load('data/twitter.dict')
# load corpus iterator
mm = gensim.corpora.MmCorpus('data/twitter.mm')
# mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_en_tfidf.mm.bz2')) # use this if you compressed the TFIDF output

print(mm)

lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=40, alpha=0.001, eval_every=5, passes=100)

lda.print_topics(20)

lda.save('data/lda.model')
