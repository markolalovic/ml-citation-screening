#!/usr/bin/python3
# prepare-longevity-data.py - Prepares data about papers and saves it to
# ..data/data.json as a json file

from pymed import PubMed
import datetime
import json

def query_pubmed(search_term='longevity'):
    '''
    Using pymed API query PubMed database
    '''
    pubmed = PubMed(tool='MyTool', email='marko@delphikos.com')
    results = pubmed.query(search_term, max_results=2000)

    article_list = []
    for article in results:
        article_dict = article.toDict()
        article_list.append(article_dict)

    return article_list

def extract_data(article_list):
    data = {}
    data['articles'] = []

    '''Extract data from search results'''
    keywords_all = set()
    for article in article_list:
        # what data we want
        pubmed_id = ''
        title = ''
        authors = ''
        publication_date = ''
        keywords = ''

        if 'pubmed_id' in article.keys():
            if '\n' in article['pubmed_id']:
                pubmed_id = article['pubmed_id'].split('\n')[0]
            else:
                pubmed_id = article['pubmed_id']

        if 'title' in article.keys():
            title = article['title']
            title = title.replace(u'\xa0', u' ')

        if 'authors' in article.keys():
            authors_list = article['authors']
            authors_string = ''
            for author in authors_list:
                if author['initials']:
                    authors_string += author['initials'] + '. '
                if author['lastname']:
                    authors_string += author['lastname']
                authors_string += ', '
            authors = authors_string[:-2]

        if 'publication_date' in article.keys():
            if isinstance(article['publication_date'], datetime.date):
                publication_date = article['publication_date'].strftime('%Y-%m-%d')
            else:
                publication_date = article['publication_date']

        if 'keywords' in article.keys():
            keywords_list = article['keywords']
            if keywords_list:
                keywords = ', '.join(article['keywords'])
                for keyword in keywords_list:
                    keywords_all.add(keyword)

        data['articles'].append({
            'pubmed_id': pubmed_id,
            'title': title,
            'authors': authors,
            'publication_date': publication_date,
            'keywords': keywords
        })

    return data

if __name__ == '__main__':
    dq_search_term = 'dasatinib AND (side effect* OR adverse event* OR adverse effect* OR risk*)'
    article_list = query_pubmed(dq_search_term)
    data = extract_data(article_list)

    with open('../data/data.json', 'w') as outfile:
        json.dump(data, outfile)

    print('Saved: '
     + str(len(data['articles'])) +
     ' as JSON file to ..data/data.json: ')
    print(data['articles'][0])
    print('...')
    print(data['articles'][-1])
