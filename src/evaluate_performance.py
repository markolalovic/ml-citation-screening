#!/usr/bin/python3
''' evaluate_performance.py - Runs stratified stratified CV to evaluate the models.
Reports precision, recall, PR AUC, WSS@R and draws WSS and PR-curves. Estimates
the performance over the folds from CV.

## First Results:

Overall recall: 0.88
Overall precision: 0.24

Mean recall: 0.88 (0.07)
Mean precision: 0.25 (0.03)
Mean PR AUC: 0.42 (0.10)
Mean WSS@R: 0.68 (0.06)

Evaluation report:
 fold  train_0  train_1  test_0  test_1   param_C  support  recall  precision  prauc   wss
    1     2150      122     538      31  1.10e-02       19    0.77       0.23   0.28  0.59
    2     2150      123     538      30  6.00e-03       12    0.93       0.21   0.48  0.70
    3     2150      123     538      30  6.00e-03        9    0.90       0.25   0.47  0.71
    4     2151      122     537      31  6.00e-03        9    0.94       0.27   0.36  0.74
    5     2151      122     537      31  1.30e-02       21    0.84       0.28   0.53  0.68
'''

import preprocess_articles as myprep
import features_extraction as myfeatures

import numpy as np
import pandas as pd
from numpy import mean, std
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, GridSearchCV, StratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.metrics import make_scorer
from sklearn.metrics import recall_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc
from sklearn.feature_selection import SelectFromModel
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
import sys


RSTATE = 42
NFOLDS = 5
CUTOFF = 0.5

hist_fig, hist_axes = plt.subplots(1, NFOLDS, figsize=(20, 5))
impo_fig, impo_axes = plt.subplots(1, NFOLDS, figsize=(20, 5))

pd.set_option('display.precision', 2)
mpl.use('pdf')


def mean_performance(cfmat):
    ''' Calculates mean performance accross all folds from combined confusion matrix.'''

    cfmat = cfmat / NFOLDS
    TN, FP, FN, TP = cfmat[0, 0], cfmat[0, 1], cfmat[1, 0], cfmat[1, 1]
    recall = TP / (TP + FN)
    precision = TP / (TP + FP)

    print('\nOverall recall: %.2f' % recall)
    print('Overall precision: %.2f' % precision)

def get_performance(results):
    ''' Calculates mean performance accross all folds.'''

    aggs = results.agg({
               'recall': ['mean', 'std'],
               'precision': ['mean', 'std'],
               'prauc': ['mean', 'std'],
               'wss': ['mean', 'std']})

    int_columns = ['train_0', 'train_1', 'test_0', 'test_1', 'fold', 'support']
    for column in int_columns:
        results[column] = results[column].astype(int)

    print('\nMean recall: %.2f (%.2f)' %
        (aggs['recall']['mean'], aggs['recall']['std']))
    print('Mean precision: %.2f (%.2f)' %
        (aggs['precision']['mean'], aggs['precision']['std']))
    print('Mean PR AUC: %.2f (%.2f)' %
        (aggs['prauc']['mean'], aggs['prauc']['std']))
    print('Mean WSS@R: %.2f (%.2f)' %
        (aggs['wss']['mean'], aggs['wss']['std']))

    return aggs

def get_step_function(x, y):
    ''' From x, y extracts starts and ends of intervals and returns only the
    pairs (x, y) where the y value changes and adds points (0, 0), (1, 1). '''

    x, y = np.array(x), np.array(y)
    y_values = list(set(y))

    y_starts = [np.where(y == y_value)[0][0] for y_value in y_values]
    y_ends = [np.where(y == y_value)[0][-1] for y_value in y_values]
    y_indices = y_starts + y_ends
    y_indices = np.array(y_indices)

    x, y = x[y_indices], y[y_indices]
    x, y = x[np.argsort(x)], y[np.argsort(x)]

    x, y = np.append([0], x), np.append([0], y)
    x, y = np.append(x, [1]), np.append(y, [1])

    return x, y

def show_performance(plots):
    ''' Saves WSS and PRAUC plots to: ``../report/figures/performance.pdf`.'''

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for subplot in list(plots.keys()):
        for label in list(plots[subplot].keys()):
            x, y = dict_to_arrays(plots[subplot][label])

            if subplot == 1:
                x, y = get_step_function(x, y)

            axes[1-subplot].plot(x, y, label=label)

    axes[0].set_xlabel('Articles screened')
    axes[0].set_ylabel('Cumulative Recall')
    axes[0].legend(loc='lower right', fontsize='small')
    axes[0].plot([0, 1], [0, 1], color='gray', ls='dashed')

    axes[1].set_xlabel('Recall')
    axes[1].set_ylabel('Precision')
    axes[1].legend(loc='upper right', fontsize='small')
    axes[1].axhline(y=0.05, color='gray', ls='dashed')

    plt.subplots_adjust(bottom=0.15, wspace=0.5)

    fig.savefig('../report/figures/performance.pdf')

def save_performance(plots):
    '''Saves WSS and PRAUC plots data for report:
        `../report/data/plot{1,2}_fold{1,..,5}.csv`.
    '''

    ## curves in each subplot
    curves = ['fold' + str(i) for i in list(range(1, NFOLDS+1))] + ['overall']
    for i in list(plots.keys()):
        labels = list(plots[i].keys())
        for j in range(len(labels)):
            label = labels[j]
            x, y = dict_to_arrays(plots[i][label])
            # x, y = interpolate(x, y)
            fname = '../report/data/plot' + str(i+1) + '_' + curves[j] + '.csv'
            with open(fname, 'w') as file:
                file.write('x,y\n') # header
                for x, y in list(zip(list(x), list(y))):
                    file.write('%s,%s\n' % (x, y))

def show_confusion_matrix(y_test, y_pred):
    ''' Prints confusion matrix. '''

    actual = pd.Series(y_test, name='Actual')
    predicted = pd.Series(y_pred, name='Predicted')
    confusion_matrix = pd.crosstab(actual, predicted)
    print(confusion_matrix)

def get_metrics(y_test, y_probs):
    '''Computes all metrics for precision-recall curves.'''

    precisions, recalls, _ = precision_recall_curve(y_test, y_probs)
    prauc = auc(recalls, precisions)

    y_pred = y_probs > CUTOFF
    y_pred = y_pred.astype(int)

    cfmat = confusion_matrix(y_test, y_pred)
    TN, FP, FN, TP = cfmat[0, 0], cfmat[0, 1], cfmat[1, 0], cfmat[1, 1]
    recall = TP / (TP + FN)
    precision = TP / (TP + FP)
    wss = (TN + FN) / len(y_test) - (1 - recall)

    return {'precisions': precisions, 'recalls': recalls, # for PR-curves
            'precision': precision, 'recall': recall,
            'prauc': prauc, 'wss': wss, 'cfmat': cfmat}

def draw_histogram(probs, fold):
    ''' Draws histogram of predicted probabilities distribution. '''

    hist_axes[fold].hist(probs, density=False, bins=30)
    hist_axes[fold].axvline(x=CUTOFF, color='red')
    hist_axes[fold].set_ylabel('Count')
    hist_axes[fold].set_xlabel('Relevance');

    if fold == NFOLDS - 1:
        hist_fig.savefig('../report/figures/probabilities.pdf')

def draw_importance(features, importance, fold, num_of_features=10):
    ''' Draws feature importance. '''

    inds = (-importance).argsort()[:num_of_features]
    inds = inds[::-1]

    importance = importance[inds]
    features = features[inds]
    positions = [i for i, _ in enumerate(features)]

    impo_axes[fold].barh(positions, importance)
    impo_axes[fold].set_yticks(positions)
    impo_axes[fold].set_yticklabels(features)

    if fold == NFOLDS - 1:
        impo_fig.tight_layout()
        impo_fig.savefig('../report/figures/feature-importance.pdf')

def arrays_to_dict(x, y):
    return dict(list(zip(x, y)))

def dict_to_arrays(d):
    return np.array(list(d.keys())), np.array(list(d.values()))

def get_model(X_train, y_train, param_C=0.01, tune_C=True):
    model = LogisticRegression(
                solver='liblinear',
                class_weight='balanced',
                fit_intercept=True,
                C=param_C,
                penalty='l1')

    if tune_C:
        space = dict()
        space['C'] = list(np.linspace(0.001, 0.1, num=100))
        recall_scorer = make_scorer(recall_score)

        cv_inner = KFold(n_splits=3, shuffle=True, random_state=RSTATE)
        gsearch = GridSearchCV(model, space, scoring=recall_scorer, cv=cv_inner, n_jobs=5)
        gresult = gsearch.fit(X_train, y_train)
        best_model = gresult.best_estimator_
        best_params = gresult.best_params_
        param_C = best_params['C']
        print('Best C: %.5f' % param_C)
    else:
        best_model = model.fit(X_train, y_train)

    return best_model, param_C

def get_train_test(articles_train, articles_test,
    records_train, records_test, fold, simple_features=True, train=True):

    if simple_features:
        X_train = myfeatures.get_stf(records_train)
        X_test = myfeatures.get_stf(records_test)
    else:
        X_train_stf = myfeatures.get_stf(records_train)
        X_test_stf = myfeatures.get_stf(records_test)

        X_train_ptf = myfeatures.get_ptf(articles_train)
        X_test_ptf = myfeatures.get_ptf(articles_test)

        X_train_tf_idf = myfeatures.get_tf_idf(records_train, fold=fold, train=train)
        X_test_tf_idf = myfeatures.get_tf_idf(records_test, fold=fold)

        X_train_lda = myfeatures.get_lda(records_train, fold=fold, train=train)
        X_test_lda = myfeatures.get_lda(records_test, fold=fold)

        X_train = myfeatures.combine([X_train_ptf, X_train_stf, X_train_tf_idf,  X_train_lda])
        X_test = myfeatures.combine([X_test_ptf, X_test_stf, X_test_tf_idf,  X_test_lda])

        X_train, X_test = myfeatures.scale(X_train, X_test)

    return X_train, X_test

def evaluate_model(simple_features):
    '''Evaluates using cross validation.'''

    ## save performance results in a data frame
    results = pd.DataFrame(columns=[
        'fold', 'train_0', 'train_1', 'test_0', 'test_1', # show fold split
        'param_C', 'support',                             # of LR model
        'recall', 'precision', 'prauc', 'wss'])           # performance metrics

    ## estimate average from confusion matrices
    cfmat_overall = np.zeros((2, 2))

    articles, records, y = myprep.load_data()

    ## save plots
    plots = {}
    plots[0] = {}
    plots[1] = {}

    ## cross validation loop
    y_probs_all = []
    y_test_all = []
    strafold = StratifiedKFold(n_splits=NFOLDS, shuffle=True, random_state=RSTATE)
    for fold, (i_train, i_test) in enumerate(strafold.split(records, y)):
        print('\nFold: %d' % (fold+1))

        y_train = y[i_train]
        y_test = y[i_test]

        records_train = [records[i] for i in list(i_train)]
        records_test = [records[i] for i in list(i_test)]

        articles_train = [articles[i] for i in list(i_train)]
        articles_test = [articles[i] for i in list(i_test)]

        X_train, X_test = get_train_test(articles_train, articles_test,
            records_train, records_test, fold, simple_features)

        best_model, param_C = get_model(X_train, y_train)

        selector = SelectFromModel(best_model, prefit=True)

        ## feature importance
        model_coefs = list(best_model.coef_[0])

        ## selected features
        features_mask = selector.get_support()
        selected_features = list(X_train.columns[features_mask])

        print('\nSelected features: ')
        print(selected_features)

        # feature importance
        draw_importance(
            features=np.array(list(X_train.columns)),
            importance=np.array(model_coefs),
            fold=fold)

        ## interpretation
        # print('\nLR coefficients: ')
        # print([model_coefs[i] for i in range(len(model_coefs)) if features_mask[i]])

        ## predict
        y_probs = best_model.predict_proba(X_test)

        y_probs = y_probs[:, 1]
        draw_histogram(y_probs, fold)

        y_probs_all.append(y_probs)
        y_test_all.append(y_test)

        metrics = get_metrics(y_test, y_probs)
        cfmat_overall += metrics['cfmat']

        ## apply order of probs to y_test - reversed from most probable to least
        y_test_list = list(y_test)
        y_probs_list = list(y_probs)

        y_test_sorted = [x for _,x in sorted(zip(y_probs_list, y_test_list), reverse=True)]
        ks = list(range(1, len(y_test) + 1))
        screened_at_k = list(map(lambda k: k/len(y_test), ks))
        recall_at_k = list(map(lambda k: sum(y_test_sorted[0:k])/sum(y_test), ks))

        lab = 'Fold %d PR AUC=%.2f' % (fold+1, metrics['prauc'])
        plots[0][lab] = arrays_to_dict(metrics['recalls'], metrics['precisions'])

        lab = 'Fold %d WSS@%.2f=%.2f' % (fold+1, metrics['recall'], metrics['wss'])
        plots[1][lab] = arrays_to_dict(screened_at_k, recall_at_k)

        print('\nRecall: %.2f' % metrics['recall'])
        print('Precision: %.2f' % metrics['precision'])

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

    mean_performance(cfmat_overall)

    ## concatenate all probs and tests
    y_probs_all = np.concatenate(y_probs_all)
    y_test_all = np.concatenate(y_test_all)
    precision_all, recall_all, _ = precision_recall_curve(y_test_all, y_probs_all)

    ## estimate ranking performance
    y_test_list = list(y_test_all)
    y_probs_list = list(y_probs_all)

    y_test_sorted = [x for _,x in sorted(zip(y_probs_list, y_test_list), reverse=True)]
    ks = list(range(1, len(y_test_list) + 1))
    screened_at_k = list(map(lambda k: k/len(y_test_list), ks))
    recall_at_k = list(map(lambda k: sum(y_test_sorted[0:k])/sum(y_test_list), ks))

    ## estimate precision-recall curve
    lab = 'Overall PR AUC=%.2f' % (auc(recall_all, precision_all))
    plots[0][lab] = arrays_to_dict(recall_all, precision_all)

    metrics_all = get_metrics(y_test_all, y_probs_all)
    lab = 'Overall WSS@%.2f=%.2f' % (metrics_all['recall'], metrics_all['wss'])
    plots[1][lab] = arrays_to_dict(screened_at_k, recall_at_k)

    return results, plots


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        simple_features = False
        print('Evaluating the full model ...')
    else:
        simple_features = True
        print('Evaluating the simple model ...')

    results, plots = evaluate_model(simple_features=simple_features)

    get_performance(results)
    show_performance(plots)
    save_performance(plots)

    print('\nEvaluation report: ')
    print(results.to_string(index=False))
