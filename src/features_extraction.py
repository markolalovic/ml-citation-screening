#!/usr/bin/python3
''' features_extraction.py - Contains all the functions for extracting features:

    - get_stf(records): 1 if search term in abstract or title for each search term
    - get_ptf(articles): 1 if publication type in main publication types for each publication type
    - get_tf_idf(records, fold): TF-IDF matrix from BoW
    - get_lda(records, fold): Distribution of LDA weights

Also: combine(dataframes) and scale(X_train, X_test).
'''

import preprocess_articles as myprep

import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import gensim
from gensim.models.wrappers import LdaMallet


mallet_path = './Mallet/bin/mallet'

search_terms = 'dasatinib AND (senolytic OR senescent) dasatinib AND quercetin \
Dasatinib AND (side effect* OR adverse event* OR adverse effect* OR safety OR risk*) \
(quercetin AND (side effect* OR adverse effect* OR adverse event* OR risk)) \
quercetin AND (senolytic OR senescent OR senescence)'

RSTATE = 42

def get_stf(records):
    ''' Returns search term based features:
            1 if search term in abstract or title for each search term.'''

    ## preprocess search terms the same way as articles
    st_parsed_filtered = myprep.parse_filter(search_terms)
    st_lemmatized = myprep.lemmatize(st_parsed_filtered)
    st_all = st_lemmatized.split(' ') + myprep.add_title_label(st_lemmatized).split(' ')

    st_all = list(set(st_all))

    X = []
    for record in records:
        words = record.split(' ')
        x = np.zeros(len(st_all))

        for j in range(len(st_all)):
            if st_all[j] in words:
                x[j] = 1

        X.append(x)

    X = np.array(X)

    def rename(term):
        '''Renames the features for interpretation.'''

        if 'title' in term:
            return term[6:] + '_in_title'
        else:
            return term + '_in_abstract'

    return pd.DataFrame(data=X[0:, 0:],
                        index=[i for i in range(X.shape[0])],
                        columns=list(map(rename, st_all)))

def get_ptf(articles):
    ''' Returns publication type based features:
            1 if publication type in publication types for each type.'''

    # case reports, clinical trials are mostly relevant and reviews irrelevant
    pt_all = ['Case Report', 'Clinical Trial', 'Revie']

    X = []
    for article in articles:
        publication_types = article['publication_types']

        x = np.zeros(len(pt_all))
        for j in range(len(pt_all)):
            if pt_all[j] in publication_types:
                x[j] = 1

        X.append(x)

    X = np.array(X)

    return pd.DataFrame(data=X[0:, 0:],
                        index=[i for i in range(X.shape[0])],
                        columns=[pt.lower().replace(' ', '_') for pt in pt_all])

def get_tf_idf(records, fold, train=False, max_features=50):
    ''' Returns TF-IDF matrix from BoW. '''

    if train:
        vectorizer = TfidfVectorizer(
                        max_features=max_features,
                        ngram_range=(2, 2), # TODO: select ngrams
                        max_df=0.5,  # TODO: chose to ignore terms that appear in more than max_df of documents
                        min_df=0.01, # TODO: chose to ignore terms that appear in less than min_df of documents
                        sublinear_tf=True  ## apply 1 + log(tf) scaling (default=False)
                     )

        ## BoW and TF-IDF
        vectorizer.fit_transform(records)
        X = vectorizer.transform(records)

        with open('../models/vectorizer-' + str(fold) + '.pickle', 'wb') as fp:
            pickle.dump(vectorizer, fp)
    else:
        with open('../models/vectorizer-' + str(fold) + '.pickle', 'rb') as fp:
            vectorizer = pickle.load(fp)

    X = vectorizer.transform(records)
    X = X.todense()

    feature_names = vectorizer.get_feature_names()
    feature_names = list(map(lambda x: 'tf-idf_' + x.replace(' ', '_'), feature_names))

    return pd.DataFrame(data=X[0:,0:],
                        index=[i for i in range(X.shape[0])],
                        columns=feature_names)

def get_lda(records, fold, train=False, num_topics=50):
    texts = [record.split(' ') for record in records]

    if train:
        id2word = gensim.corpora.Dictionary(texts) # create dictionary

        ## filter out tokens that appear in:
        id2word.filter_extremes(
                    no_below=20, # less than no_below documents: 20
                    no_above=0.4 # more than no_above documents: 0.4
                )

        id2word.compactify()

        corpus = [id2word.doc2bow(text) for text in texts]

        lda_model = LdaMallet(
                        mallet_path,
                        corpus=corpus,
                        num_topics=num_topics,
                        alpha=10, # the number of topics documents are made up of
                        id2word=id2word)

        ## calculate coherence for model evaluation
        coherence_model = gensim.models.coherencemodel.CoherenceModel(
                                                        model=lda_model,
                                                        texts=texts,
                                                        dictionary=id2word,
                                                        coherence='c_v')

        coherence = coherence_model.get_coherence()
        print('Coherence of LDA model:  %.2f' % coherence)

        ## save dictionary and lda model
        with open('../models/id2word-' + str(fold) + '.pickle', 'wb') as fp:
            pickle.dump(id2word, fp)
        with open('../models/lda_model-' + str(fold) + '.pickle', 'wb') as fp:
            pickle.dump(lda_model, fp)
    else:
        ## load dictionary and lda model
        with open('../models/id2word-' + str(fold) + '.pickle', 'rb') as fp:
            id2word = pickle.load(fp)
        with open('../models/lda_model-' + str(fold) + '.pickle', 'rb') as fp:
            lda_model = pickle.load(fp)

        corpus = [id2word.doc2bow(text) for text in texts]

    ## for interpretation
    # topics = lda_model.show_topics(num_topics=-1, formatted=False)
    # topics = list(map(lambda topic: ' '.join([x[0] for x in topic[1]]), topics))

    ## extract distribution for each document
    X = []
    for distribution in lda_model[corpus]:
        indices = [tup[0] for tup in distribution]
        weights = [tup[1] for tup in distribution]

        x = np.zeros(num_topics)
        x[np.array(indices)] = np.array(weights)

        X.append(x)

    X = np.array(X)

    return pd.DataFrame(
                data=X[0: ,0: ],
                index=[i for i in range(X.shape[0])],
                columns=['lda_' + str(i) for i in range(num_topics)])

def combine(dataframes):
    ''' Combines dataframes in one Pandas DataFrame. '''

    for i in range(len(dataframes) - 1):
        dataframes[i] = dataframes[i].reset_index(drop=True)

    return pd.concat(dataframes, axis=1)

def scale(X_train, X_test):
    ''' Standardize features in X_train and X_test. '''

    std_scaler = StandardScaler(with_mean=True)

    X_train_scaled = std_scaler.fit_transform(X_train)
    X_test_scaled = std_scaler.transform(X_test)

    X_train = pd.DataFrame(
        X_train_scaled, index=X_train.index, columns=X_train.columns)

    X_test = pd.DataFrame(
        X_test_scaled, index=X_test.index, columns=X_test.columns)

    return X_train, X_test
