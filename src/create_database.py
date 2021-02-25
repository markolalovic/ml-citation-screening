#!/usr/bin/python3
''' create_database.py - Creates a database of records from articles for
Dasatinib & Quercetin Senolytic Therapy Risk-Benefit Analysis
https://www.forever-healthy.org/news/risk-benefit-analysis-of-dasatinib-quercetin-as-a-senolytic-therapy

## Steps:

    - queries PubMed using the specified search terms;
    - scrapes titles and abstracts from PubMed since the API truncated some abstracts;
    - adds missing relevant articles from `missing_articles.json`;
    - labels articles using `relevant_titles.csv`;
    - creates mysql database longevity_research.sql;

## Results of queries to PubMed using the search terms:

    Number of articles for search terms:
    dasatinib AND (senolytic OR senescent): 46
    dasatinib AND quercetin: 47
    Dasatinib AND (side effect* OR adverse event* OR adverse effect* OR safety OR risk*): 1197
    (quercetin AND (side effect* OR adverse effect* OR adverse event* OR risk)): 1712
    quercetin AND (senolytic OR senescent OR senescence): 422
    -------------------------------------------------------------------------------------------
    Total number of unique articles: 3248

## Database:

    $ mysql -u root -p longevity_research < ./data/longevity_research.sql
    Enter password: password

    $ mysql -u root -p
    mysql> use longevity_research;

    mysql> show tables;
    +-------------------------------------------+
    | Tables_in_longevity_research              |
    +-------------------------------------------+
    | dasatinib_and_quercetin_senolytic_therapy |
    +-------------------------------------------+
    1 row in set (0.01 sec)

    mysql> describe dasatinib_and_quercetin_senolytic_therapy;
    +-------------------+------+------+-----+---------+-------+
    | Field             | Type | Null | Key | Default | Extra |
    +-------------------+------+------+-----+---------+-------+
    | url               | text | YES  |     | NULL    |       |
    | publication_date  | date | YES  |     | NULL    |       |
    | publication_types | text | YES  |     | NULL    |       |
    | title             | text | YES  |     | NULL    |       |
    | abstract          | text | YES  |     | NULL    |       |
    | relevant          | int  | YES  |     | NULL    |       |
    +-------------------+------+------+-----+---------+-------+
    6 rows in set (0.01 sec)

    mysql> select count(*) from dasatinib_and_quercetin_senolytic_therapy;
    +----------+
    | count(*) |
    +----------+
    |     3259 |
    +----------+
    1 row in set (0.01 sec)

    mysql> select count(if(relevant = 1, 1, NULL)) from
    dasatinib_and_quercetin_senolytic_therapy;
    +----------------------------------+
    | count(if(relevant = 1, 1, NULL)) |
    +----------------------------------+
    |                              153 |
    +----------------------------------+
    1 row in set (0.01 sec)

'''

from pymed import PubMed
from datetime import datetime
import pickle
import json
import mysql.connector
import numpy as np
import pandas as pd
import time
from selenium import webdriver
import random


search_terms = [
    'dasatinib AND (senolytic OR senescent)',
    'dasatinib AND quercetin',
    'Dasatinib AND (side effect* OR adverse event* OR adverse effect* OR safety OR risk*)',
    '(quercetin AND (side effect* OR adverse effect* OR adverse event* OR risk))',
    'quercetin AND (senolytic OR senescent OR senescence)']

path_to_chrome_driver = '../tools/chromedriver'

def query_pubmed(search_term, max_results=5000):
    ''' Uses pymed API to query PubMed database. '''

    pubmed = PubMed(tool='MyTool', email='')
    results = pubmed.query(search_term, max_results=max_results)

    article_list = []
    for article in results:
        article_dict = article.toDict()
        article_list.append(article_dict)

    return article_list

def extract_data(article_list):
    ''' Extracts PubMedIDs and publication dates from search results in
        `article_list`. '''

    extracted = {}
    for article in article_list:
        pubmed_id = ''
        publication_date = ''
        if 'pubmed_id' in article.keys():
            pubmed_id = article['pubmed_id']
        if 'publication_date' in article.keys():
            publication_date = str(article['publication_date'])

        if pubmed_id:
            if '\n' in pubmed_id:
                pubmed_id = pubmed_id.split('\n')[0]
            extracted[pubmed_id] = publication_date # unique since we are using dictionary

    return extracted

def scrape_record(url, driver):
    ''' Scrapes title and abstract from PubMed using PubMedID. '''

    title_text = ''
    abstract_text = ''

    driver.implicitly_wait(random.randint(1, 2))
    driver.get(url)
    title_elt = driver.find_elements_by_class_name('heading-title')
    for value in title_elt:
        title_text += value.text

    abstract_elt = driver.find_elements_by_xpath('//*[@id="enc-abstract"]')
    for value in abstract_elt:
        abstract_text += value.text

    return title_text, abstract_text

def scrape_publication_types(url, driver):
    ''' Scrapes publication types from PubMed using PubMedID. '''

    publication_types_text = ''

    driver.implicitly_wait(random.randint(1, 2))
    driver.get(url)
    publication_types_element = driver.find_elements_by_xpath(
        '//*[@id="publication-types"]/ul/li/div/button')

    for value in publication_types_element:
        publication_types_text += value.text + ';'

    return publication_types_text

def estimate_scraping_time(n, a=1, b=2):
    ''' Prints estimated web scraping time for n articles when setting waiting
    time to random.randint(a, b) to avoid many requests in short time. '''

    wait_times_df = pd.DataFrame({'wait_times': [random.randint(a, b) for i in range(n)]})
    cross_tab = pd.crosstab(index=wait_times_df["wait_times"], columns="count")
    cross_tab = cross_tab.to_numpy()
    estimated_time = (cross_tab[0][0] + cross_tab[1][0]*2) / 60

    print('Estimated scraping time: %dh %dmin'
        % (int(estimated_time // 60), int(estimated_time % 60)))

def print_number_of_articles(query_results_dict):
    ''' Checks the numbers of articles for search terms.'''

    print('\nNumber of articles for search terms:')
    for search_term in query_results_dict.keys():
        print(search_term + ': ' \
            + str(len(query_results_dict[search_term])))

    query_results = get_query_results(query_results_dict)
    pubmed_ids = list(query_results.keys())
    publication_dates = list(query_results.values())

    print('\nTotal number of unique articles: ' + str(len(query_results)))
    print('\nArticles: %s, ...,\n\t %s' % \
        (str(dict(list(query_results.items())[:3]))[1:-1],
        str(dict(list(query_results.items())[-3:]))[1:-1]))

def get_query_results(query_results_dict):
    ''' Flattens and removes duplicates.'''

    query_results = list(query_results_dict.values())

    result = {}
    for d in query_results:
        result.update(d)

    return result

def get_query_results_dict(run_query=False):
    ''' Queries PubMed using search_terms. '''

    if run_query:
        query_results_dict = {}
        for search_term in search_terms:
            article_list = query_pubmed(search_term)
            query_results_dict[search_term] = extract_data(article_list)

        with open('../data/query_results_dict.pickle', 'wb') as fp:
            pickle.dump(query_results_dict, fp)
    else:
        with open('../data/query_results_dict.pickle', 'rb') as fp:
            query_results_dict = pickle.load(fp)

    return query_results_dict

def get_scraped_articles(query_results, scrape=False):
    ''' Scrapes PubMed for title and abstract. '''

    if scrape:
        estimate_scraping_time(len(query_results))
        scraped_articles = []
        driver = webdriver.Chrome(path_to_chrome_driver)
        for pubmed_id, publication_date in query_results.items():
            url = 'https://pubmed.ncbi.nlm.nih.gov/' + str(pubmed_id) + '/'
            title, abstract = scrape_record(url, driver)
            scraped_articles.append({
                'url': url,
                'publication_date': publication_date,
                'title': title,
                'abstract': abstract})

        driver.quit()
        with open('../data/scraped_articles.pickle', 'wb') as fp:
            pickle.dump(scraped_articles, fp)
    else:
        with open('../data/scraped_articles.pickle', 'rb') as fp:
            scraped_articles = pickle.load(fp)

    return scraped_articles

def add_publication_types(scraped_articles, scrape=False):
    ''' Scrapes PubMed for publication types. '''

    if scrape:
        estimate_scraping_time(len(scraped_articles))
        driver = webdriver.Chrome(path_to_chrome_driver)
        for article in scraped_articles:
            pubmed_id = article['url'].split('/')[-2]
            url = 'https://pubmed.ncbi.nlm.nih.gov/' + pubmed_id + '/'
            publication_types = scrape_publication_types(url, driver)
            article['publication_types'] = publication_types

        driver.quit()
        with open('../data/scraped_articles_publication_types.pickle', 'wb') as fp:
            pickle.dump(scraped_articles, fp)
    else:
        with open('../data/scraped_articles_publication_types.pickle', 'rb') as fp:
            scraped_articles = pickle.load(fp)

    return scraped_articles

def get_missing_articles():
    ''' Loads missing relevant articles. '''

    with open('../data/missing_articles.json') as json_file:
        missing_articles = json.load(json_file)

    return list(missing_articles.values())

def get_article_by_title(articles, title):
    ''' Returns first matched article. '''

    for article in articles:
        if article['title'] == title:
            return article

def get_unique_articles(all_articles):
    ''' Removes duplicates from all_articles by title.
    Skips one dupicate retrieved from PubMed with different PubMedID:

    Imatinib Mesylate: 'https://pubmed.ncbi.nlm.nih.gov/24756783/'
    Imatinib mesylate: 'https://pubmed.ncbi.nlm.nih.gov/30069623/'
    '''

    titles = list(map(lambda article: article['title'], all_articles))
    titles.remove('Imatinib Mesylate')
    unique_titles = list(set(titles))

    articles = []
    for unique_title in unique_titles:
        articles.append(get_article_by_title(all_articles, unique_title))

    return articles

def fix_dates(articles):
    ''' Creates dates with January 1st for 8 cases with only year stated:
            2015, 2006, 2006, 2015, 2011, 2006, 2020, 2006. '''

    for article in articles:
        publication_date = article['publication_date']
        if '-' in publication_date:
            year, month, day = publication_date.split('-')
            article['publication_date'] = datetime(int(year), int(month), int(day))
        else:
            article['publication_date'] = datetime(int(publication_date), 1, 1)

def label_articles(articles):
    ''' Labels articles. '''

    relevant_titles = pd.read_csv('../data/relevant_titles.csv', sep='|')
    relevant_titles = list(relevant_titles['title'])

    for article in articles:
        if article['title'] in relevant_titles:
            article['relevant'] = 1
        else:
            article['relevant'] = 0

def remove_missing(articles):
    ''' Remove articles with missing abstracts. '''

    complete = []
    for article in articles:
        if article['abstract']:
            complete.append(article)

    return complete

def create_database():
    ''' Creates `longevity_research` database and
    `dasatinib_and_quercetin_senolytic_therapy` table:

        For each article inserts:
            url, publication_date, title, abstract, relevant
        into:
            `dasatinib_and_quercetin_senolytic_therapy` table in longevity_research db

        Dump the database in ./data:
        $ mysqldump -u root -p longevity_research > ./data/longevity_research.sql
    '''

    cnx = mysql.connector.connect(user='root',
                                  password='password',
                                  host='127.0.0.1')
    cursor = cnx.cursor()
    cursor.execute('CREATE DATABASE longevity_research')
    cursor.execute('USE longevity_research')
    cursor.execute('CREATE TABLE dasatinib_and_quercetin_senolytic_therapy \
        (url TEXT, publication_date DATE, publication_types TEXT, \
        title TEXT, abstract TEXT, relevant INT)')
    cursor.execute('DESCRIBE dasatinib_and_quercetin_senolytic_therapy')

    for field in cursor:
        print(field)

    cursor.close()
    cnx.close()

def insert_mysql(articles):
    '''
    ## dump the created database to data:
    # $ mysqldump -u root -p longevity_research > ../data/longevity_research.sql'

    TODO: upload longevity_research db to Zenodo.
    '''

    cnx = mysql.connector.connect(user='root',
                                  password='password',
                                  host='127.0.0.1',
                                  database='longevity_research')

    add_record = ('INSERT INTO dasatinib_and_quercetin_senolytic_therapy '
                  '(url, publication_date, publication_types, title, abstract, relevant) '
                  'VALUES (%s, %s, %s, %s, %s, %s)')

    cursor = cnx.cursor()

    for article in articles:
        data_record = (article['url'],
                       article['publication_date'],
                       article['publication_types'],
                       article['title'],
                       article['abstract'],
                       article['relevant'])
        cursor.execute(add_record, data_record)
        emp_no = cursor.lastrowid
        cnx.commit()

    cursor.close()
    cnx.close()

if __name__ == '__main__':
    query_results_dict = get_query_results_dict(run_query=False)
    print_number_of_articles(query_results_dict)

    query_results = get_query_results(query_results_dict)
    scraped_articles = get_scraped_articles(query_results, scrape=False)
    scraped_articles = add_publication_types(scraped_articles, scrape=False)

    missing_articles = get_missing_articles()
    all_articles = missing_articles + scraped_articles
    articles = get_unique_articles(all_articles)

    fix_dates(articles)
    label_articles(articles)

    articles = remove_missing(articles)
    y = np.array(list(map(lambda article: article['relevant'], articles)))

    print('Number of articles: %d' % len(articles)) # 3106
    print('Number of relevant articles: %d' % sum(y)) # 153

    create_database()
    insert_mysql(articles)
    print('Created database: `../data/longevity_research.sql`.')
