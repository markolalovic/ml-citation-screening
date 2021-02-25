#!/usr/bin/python3
''' export_results.py - Exports relevances for new articles for update and
tables of misclassified articles for error analysis:

../src/table{New, FalseNegatives, FalsePositives}Articles.js


## Error Analysis:

Mean recall: 0.87 (0.07)
Mean precision: 0.26 (0.03)
Mean PR AUC: 0.43 (0.09)
Mean WSS@R: 0.69 (0.07)

Evaluation report:
 fold  train_0  train_1  test_0  test_1   param_C  support  recall  precision  prauc   wss
    1     2150      122     538      31  1.10e-02       18    0.77       0.23   0.28  0.59
    2     2150      123     538      30  6.00e-03       11    0.93       0.22   0.52  0.71
    3     2150      123     538      30  2.50e-02       53    0.90       0.30   0.48  0.74
    4     2151      122     537      31  6.00e-03       10    0.94       0.27   0.40  0.74
    5     2151      122     537      31  6.00e-03       11    0.81       0.27   0.46  0.64

Overall: n_FN = 20 n_FP = 389
'''

import preprocess_articles as myprep
import evaluate_performance as myeval

from sklearn.model_selection import KFold, GridSearchCV, StratifiedKFold
from datetime import date
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression
import json
import numpy as np
import pandas as pd
import sys


RSTATE = 42
NFOLDS = 5
CUTOFF = 0.5
SIMPLE_FEATURES = True

def get_error_indices(y_test, y_pred):
    '''Returns indices of false negatives and false positives for analysis.'''

    indices_FNs = list(set(np.where(y_test == 1)[0]) & set(np.where(y_pred == 0)[0]))
    indices_FPs = list(set(np.where(y_test == 0)[0]) & set(np.where(y_pred == 1)[0]))

    return {'FN': indices_FNs, 'FP': indices_FPs}

def extract_data(article, y_prob):
    '''Extracts data for one row of JSON export. '''

    url = article['url']

    date = article['publication_date']
    date = date.strftime("%d %B, %Y")

    title = article['title'].replace('\n','')
    title = title.replace("'", "")
    title = title.replace('"', '')

    abstract = article['abstract'].replace('\n','')
    abstract = abstract.replace("'", "")
    abstract = abstract.replace('"', '')

    relevance = str(np.round(y_prob, 2))

    return {'url': url, 'date': date, 'title': title, 'abstract': abstract, 'relevance': relevance}

def export_to_table(articles, y_probs, table_name):
    ''' Writes JS file for each table_name:
        ../src/table{New, FalseNegatives, FalsePositives}Articles.js
    '''

    file = open('../src/' + table_name + '.js', 'w')

    # 'let falseNegatives = [\n'
    file.write('let ' + table_name[5].lower() + table_name[6:] + ' = [\n')

    indices = np.argsort(y_probs)
    indices = list(indices)
    indices.reverse()
    for i in indices:
        article = extract_data(articles[i], y_probs[i])
        file.write('{')
        file.write('url: "' + article['url'] + '", date: "' + article['date']
            + '", title: "' + article['title'] + '", abstract: "'
            + article['abstract'] + '", relevance: "' + article['relevance'] + '"')
        file.write('},\n')

    file.write('];')
    file.close()

def check_order(articles, records):
    ''' Checks if articles and records are in the same order. '''

    print('\nOrder of articles and records: \n')

    for i in range(10):
        print(articles[i]['title'][0:40].replace('\n','') + '    ' +
              records[i][0:40].replace('\n',''))
    print()

def error_analysis():
    ''' Saves misclassified articles and relevances of each fold. '''

    articles_FN = []
    articles_FP = []
    y_probs_FN = []
    y_probs_FP = []

    articles, records, y = myprep.load_data()

    ## save performance results in a data frame
    results = pd.DataFrame(columns=[
        'fold', 'train_0', 'train_1', 'test_0', 'test_1', # show fold split
        'param_C', 'support',                             # of LR model
        'recall', 'precision', 'prauc', 'wss'])           # performance metrics

    strafold = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=RSTATE)
    for fold, (i_train, i_test) in enumerate(strafold.split(records, y)):
        print('\nFold: %d' % (fold+1))

        y_train = y[i_train]
        y_test = y[i_test]

        records_train = [records[i] for i in list(i_train)]
        records_test = [records[i] for i in list(i_test)]

        articles_train = [articles[i] for i in list(i_train)]
        articles_test = [articles[i] for i in list(i_test)]

        X_train, X_test = myeval.get_train_test(articles_train, articles_test,
            records_train, records_test, fold, simple_features=SIMPLE_FEATURES, train=True)

        best_model, param_C = myeval.get_model(X_train, y_train)

        selector = SelectFromModel(best_model, prefit=True)

        ## feature importance
        model_coefs = list(best_model.coef_[0])

        ## selected features
        features_mask = selector.get_support()
        selected_features = list(X_train.columns[features_mask])

        print('\nSelected features: ')
        print(selected_features)

        y_probs = best_model.predict_proba(X_test)
        y_probs = y_probs[:, 1]

        y_pred = y_probs > CUTOFF
        y_pred = y_pred.astype(int)

        metrics = myeval.get_metrics(y_test, y_probs)

        indices = get_error_indices(y_test, y_pred)

        articles_FN += [articles_test[i] for i in indices['FN']]
        articles_FP += [articles_test[i] for i in indices['FP']]

        y_probs_FN += [y_probs[i] for i in indices['FN']]
        y_probs_FP += [y_probs[i] for i in indices['FP']]

        results = results.append({
                'fold': fold+1,
                'train_0': len(y_train[y_train==0]),
                'train_1': len(y_train[y_train==1]),
                'test_0': len(y_test[y_test==0]),
                'test_1': len(y_test[y_test==1]),
                'param_C': param_C,
                'support': sum(selector.get_support()),
                'recall': metrics['recall'],
                'precision': metrics['precision'],
                'prauc': metrics['prauc'],
                'wss': metrics['wss']}, ignore_index=True)

    print('\nError Analysis: ')
    myeval.get_performance(results)
    print('\nEvaluation report: ')
    print(results.to_string(index=False))

    # 19 false negatives and 396 false positives
    print('\nOverall: n_FN = %d n_FP = %d' % (len(articles_FN), len(articles_FP)) )

    export_to_table(articles_FN, y_probs_FN, 'tableFalseNegatives')
    export_to_table(articles_FP, y_probs_FP, 'tableFalsePositives')

def for_update():
    ''' Builds a model on all the old articles and saves relevances for new
    articles. '''

    articles_train, records_train, y_train = myprep.load_data()
    articles_test, records_test, _ = myprep.load_data('new')

    X_train, X_test = myeval.get_train_test(articles_train, articles_test,
        records_train, records_test, fold=123, simple_features=SIMPLE_FEATURES, train=True)

    best_model, param_C = myeval.get_model(X_train, y_train, tune_C=False)
    selector = SelectFromModel(best_model, prefit=True)

    y_probs = best_model.predict_proba(X_test)
    y_probs = y_probs[:, 1]

    print('\nModel for update: ')
    print('Best C: %.2f' % param_C)
    print('Support: %d' % sum(selector.get_support()))

    export_to_table(articles_test, y_probs, 'tableNewArticles')


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        SIMPLE_FEATURES = False
        print('Exporting the full model ..')
    else:
        print('Exporting the simple model ..')

    for_update()

    error_analysis()
