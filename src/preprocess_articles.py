#!/usr/bin/python3
''' preprocess_articles.py - Preprocesses all articles, extracts and saves the records.

## Steps:
    - Load articles data from `../data/longevity_research.sql`
    and saves it to `../data/articles.pickle`;
    - Check for duplicates;
    - Preprocess articles and save the records to '../data/records.pickle';

## Results:
Number of all articles: 3104
Number of relevant articles: 153
'''

import mysql.connector
from datetime import datetime
import pickle
import numpy as np
import gensim
import spacy
from sys import argv

nlp = spacy.load("en_core_web_sm")
CUTOFF_DATE = datetime.date(datetime(2020, 4, 17)) # date of the risk benefit analysis was April 17, 2020


def get_articles(from_db=False):
    ''' Returns articles data, if from_db=True from:
        `../data/longevity_research.sql`
    else from:
        `../data/articles.pickle.` '''

    if from_db:
        database = 'longevity_research'
        table = 'dasatinib_and_quercetin_senolytic_therapy'

        cnx = mysql.connector.connect(user='root',
                                      password='password',
                                      host='127.0.0.1',
                                      database=database)

        cursor = cnx.cursor()

        query = ('SELECT url, publication_date, publication_types, title, abstract, relevant FROM ' + table)
        cursor.execute(query)

        articles = [{'url': url,
                     'publication_date': publication_date,
                     'publication_types': publication_types,
                     'title': title,
                     'abstract': abstract,
                     'relevant': relevant} for \
                     url, publication_date, publication_types, title, abstract, relevant in cursor]

        cursor.close()
        cnx.close()

        for article in articles:
            article['title'] = article['title'].replace('[', '')
            article['title'] = article['title'].replace(']', '')
            article['abstract'] = article['abstract'].replace('\n', ' ')

        del articles[1321] # remove Corrigendum: ..

        with open('../data/articles.pickle', 'wb') as fp:
            pickle.dump(articles, fp)

        print('Saved articles to `../data/articles.pickle`.')
    else:
        with open('../data/articles.pickle', 'rb') as fp:
            articles = pickle.load(fp)

    return articles

def check(articles):
    ''' Checks if there are any duplicates and prints number of articles
    and number of relevant articles. '''

    urls = list(map(lambda article: article['url'], articles))
    abstracts = list(map(lambda article: article['abstract'], articles))
    relevants = list(map(lambda article: article['relevant'], articles))

    assert len(list(set(urls))) == len(urls), 'urls are not unique!'
    assert len(list(set(abstracts))) == len(abstracts), 'abstracts are not unique!'

    y = np.array(relevants)
    print('Number of all articles: %d' % len(y))
    print('Number of relevant articles: %d' % sum(y))

def add_title_label(title_lemmatized):
    '''Adds `title_` label to words in title to separate it from abstract.'''

    tokenised = [token for token in nlp(title_lemmatized)]
    labeled = list(map(lambda x: 'title_' + str(x), tokenised))

    return ' '.join(labeled)

def keep_token(tok):
    ''' For filtering tokens by POS tags:
            PUNCT: punctuation
            NUM: numeral
            AUX: auxiliary
            DET: determiner
            PART: particle
            SYM: symbol
            ADP: adposition
            PRON: pronoun
            CCONJ: coordinating conjunction
     '''

    return tok.pos_ not in {'PUNCT', 'NUM', 'AUX', 'DET', 'PART',
                            'SYM', 'ADP', 'PRON', 'CCONJ'}

def filter_tokens(text_parsed):
    ''' Filters words defined by POS tags in keep_token(). '''

    filtered_tokens = list(filter(keep_token, text_parsed))

    filtered_tokens = [str(toc) for toc in filtered_tokens]
    text_parsed_filtered = ' '.join(filtered_tokens)

    return nlp(text_parsed_filtered)

def parse_filter(text):
    ''' Parses and filters text. '''

    text = text.replace('\n', ' ')
    text_parsed = nlp(text)
    text_parsed_filtered = filter_tokens(text_parsed)

    return text_parsed_filtered

def lemmatize(text_parsed_filtered):
    ''' Reduces the words in a given sentence to base forms. '''

    text_lemmatized = [token.lemma_.lower() for token in text_parsed_filtered]

    return ' '.join(text_lemmatized)

def get_records(articles, preprocess=False):
    ''' Preprocess title and abstract, add `title_` label and insert it at the
     beginning. '''

    if preprocess:
        records = []

        for article in articles:
            title_parsed_filtered = parse_filter(article['title'])
            abstract_parsed_filtered = parse_filter(article['abstract'])

            title_lemmatized = lemmatize(title_parsed_filtered)
            title_lemmatized = add_title_label(title_lemmatized)

            sentences_unigrams = [title_lemmatized.split(' ')]

            for sent in abstract_parsed_filtered.sents:
                sent_lemmatized = lemmatize(sent)
                sentences_unigrams.append(sent_lemmatized.split(' '))

            sentences_unigrams = [' '.join(sentences_unigram) for sentences_unigram in sentences_unigrams]

            records.append(' '.join(sentences_unigrams))

        with open('../data/records.pickle', 'wb') as fp:
            pickle.dump(records, fp)
    else:
        with open('../data/records.pickle', 'rb') as fp:
            records = pickle.load(fp)

    return records

def load_data(which='old'):
    with open('../data/articles.pickle', 'rb') as fp:
        articles = pickle.load(fp)
    with open('../data/records.pickle', 'rb') as fp:
        records = pickle.load(fp)

    split = [article['publication_date'] < CUTOFF_DATE for article in articles]

    indices = {}
    indices['old'] = [i for i, x in enumerate(split) if x]
    indices['new'] = [i for i, x in enumerate(split) if not x]

    articles = [articles[i] for i in indices[which]]
    records = [records[i] for i in indices[which]]
    y = np.array(list(map(lambda article: article['relevant'], articles)))

    return articles, records, y


if __name__ == '__main__':
    articles = get_articles(from_db=True)
    check(articles)

    print('Articles: ')
    for i in range(3, 5):
        print(articles[i]['title'] + '\n')
        print(articles[i]['abstract'] + '\n')

    records = get_records(articles, preprocess=False)

    print('Processed records: ')
    for i in range(3, 5):
        print(records[i] + '\n')
