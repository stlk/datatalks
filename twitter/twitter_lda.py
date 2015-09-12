import logging, gensim, bz2
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# load id->word mapping (the dictionary), one of the results of step 2 above
id2word = gensim.corpora.Dictionary.load('alexip_followers_py27.dict')
# load corpus iterator
mm = gensim.corpora.MmCorpus('alexip_followers_py27.mm')
# mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_en_tfidf.mm.bz2')) # use this if you compressed the TFIDF output

print(mm)

lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=10, update_every=1, chunksize=10000, passes=100)

lda.print_topics(20)

lda.save('lda.model')
