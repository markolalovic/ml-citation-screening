#!/usr/bin/python3
''' evaluate_performance.py - Runs stratified stratified CV to evaluate the models.
Reports precision, recall, PR AUC, WSS@R and draws WSS and PR-curves. Estimates
the performance over the folds from CV.

## Evaluation:

Evaluation report for CUTOFF = 0.5:
 fold train_0 train_1 test_0 test_1 param_C support       recall    precision        prauc          wss
    1    2150     122    538     31     0.1      80         0.81         0.28         0.46         0.65
    2    2150     123    538     30     0.1      83         0.77         0.22          0.4         0.59
    3    2150     123    538     30     0.1      78          0.8         0.33         0.45         0.67
    4    2151     122    537     31     0.1      81         0.84          0.3         0.58         0.69
    5    2151     122    537     31     0.1      76         0.77         0.31          0.4         0.64
 Mean    2150     122    537     30    0.10  79 (2)  0.80 (0.03)  0.29 (0.04)  0.46 (0.07)  0.65 (0.04)


Evaluation report for CUTOFF = 0.26:
 fold train_0 train_1 test_0 test_1 param_C  support       recall    precision        prauc          wss
    1    2150     122    538     31    0.01       17         0.94         0.13         0.54         0.53
    2    2150     123    538     30    0.01       19          0.9         0.16         0.33         0.61
    3    2150     123    538     30    0.01       16            1         0.14         0.48         0.63
    4    2151     122    537     31    0.04       56         0.94         0.19         0.54         0.67
    5    2151     122    537     31    0.02       35         0.97          0.2         0.43         0.71
 Mean    2150     122    537     30    0.02  28 (15)  0.95 (0.03)  0.17 (0.03)  0.46 (0.08)  0.63 (0.06)
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


RSTATE = 142
NFOLDS = 5
CUTOFF = 0.26

hist_fig, hist_axes = plt.subplots(1, NFOLDS, figsize=(20, 5))
impo_fig, impo_axes = plt.subplots(1, NFOLDS, figsize=(20, 5))

pd.set_option('display.precision', 2)
mpl.use('pdf')


def mean_performance(cfmat):
    ''' Prints mean performance across all folds from combined confusion matrix.'''

    cfmat = cfmat / NFOLDS
    TN, FP, FN, TP = cfmat[0, 0], cfmat[0, 1], cfmat[1, 0], cfmat[1, 1]
    recall = TP / (TP + FN)
    precision = TP / (TP + FP)

    print('\nOverall recall: %.2f' % recall)
    print('Overall precision: %.2f' % precision)

def add_mean_performance(results):
    ''' Adds mean performance across all folds from results matrix, returns it
    and saves it to: `../report/data/evaluation_report_results.csv` '''

    int_columns = ['fold', 'train_0', 'train_1', 'test_0', 'test_1', 'support']
    for column in int_columns:
        results[column] = results[column].astype(int)

    means = np.mean(np.array(results), axis=0)
    stds = np.std(np.array(results), axis=0)

    results = results.round(2)

    results = results.append(
        {
            'fold': 'Mean',
            'train_0': '%d' % means[1],
            'train_1': '%d' % means[2],
            'test_0': '%d' % means[3],
            'test_1': '%d' % means[4],
            'param_C': '%.2f' % means[5],
            'support': '%d (%d)' % (means[6], stds[6]),
            'recall': '%.2f (%.2f)' % (means[7], stds[7]),
            'precision': '%.2f (%.2f)' % (means[8], stds[8]),
            'prauc': '%.2f (%.2f)' % (means[9], stds[9]),
            'wss': '%.2f (%.2f)' % (means[10], stds[10]),
        }, ignore_index=True)

    results.to_csv(r'../report/data/evaluation_report_results.csv', index=False)

    return results

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

def show_performance(plots, simple_features):
    ''' Saves WSS and PRAUC plots to: ``../report/figures/performance.pdf`.'''

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for subplot in list(plots.keys()):
        for label in list(plots[subplot].keys()):

            x, y = dict_to_arrays(plots[subplot][label])

            if subplot == 1:
                x, y = get_step_function(x, y)

            axes[subplot].plot(x, y, label=label)

    axes[0].set_xlabel('Recall')
    axes[0].set_ylabel('Precision')
    axes[0].legend(loc='upper right', fontsize='small')
    axes[0].axhline(y=0.05, color='gray', ls='dashed')
    axes[0].vlines(x=.95, ymin=0, ymax=1, ls='dotted', color='grey')

    axes[1].set_xlabel('Articles screened')
    axes[1].set_ylabel('Cumulative Recall')
    axes[1].legend(loc='lower right', fontsize='small')
    axes[1].plot([0, 1], [0, 1], color='gray', ls='dashed')
    axes[1].hlines(y=.95, xmin=0, xmax=1, ls='dotted', color='gray')
    axes[1].vlines(x=.45, ymin=0, ymax=1, ls='dotted', color='grey')

    plt.subplots_adjust(bottom=0.15, wspace=0.5)

    if simple_features:
        fig.savefig('../report/figures/performance-simple.pdf')
    else:
        fig.savefig('../report/figures/performance-full.pdf')

def save_performance(plots, simple_features):
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

            if i == 1:
                x, y = get_step_function(x, y)

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

def draw_histogram(probs, fold, simple_features):
    ''' Draws histogram of predicted probabilities distribution. '''

    hist_axes[fold].hist(probs, density=False, bins=30)
    hist_axes[fold].axvline(x=CUTOFF, color='red')
    hist_axes[fold].set_ylabel('Count')
    hist_axes[fold].set_xlabel('Relevance');

    if fold == NFOLDS - 1:
        if simple_features:
            hist_fig.savefig('../report/figures/probabilities-simple.pdf')
        else:
            hist_fig.savefig('../report/figures/probabilities-full.pdf')

def draw_feature_importance(features, importance,
        fold, simple_features, num_of_features=10):
    ''' Draws the feature importance. '''

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
        if simple_features:
            impo_fig.savefig('../report/figures/feature-importance-simple.pdf')
        else:
            impo_fig.savefig('../report/figures/feature-importance-full.pdf')

def arrays_to_dict(x, y):
    return dict(list(zip(x, y)))

def dict_to_arrays(d):
    return np.array(list(d.keys())), np.array(list(d.values()))

def get_model(X_train, y_train, param_C=0.03, tune_C=True):
    model = LogisticRegression(
                solver='liblinear',
                class_weight='balanced',
                fit_intercept=True,
                C=param_C,
                penalty='l1')

    if tune_C:
        space = dict()
        space['C'] = list(np.linspace(0.01, 1, num=200))
        recall_scorer = make_scorer(recall_score)

        cv_inner = KFold(n_splits=3, shuffle=True, random_state=RSTATE)

        gsearch = GridSearchCV(
            model, space, cv=cv_inner,
            scoring=recall_scorer,
            n_jobs=5)

        gresult = gsearch.fit(X_train, y_train)
        best_model = gresult.best_estimator_
        best_params = gresult.best_params_
        param_C = best_params['C']
        print('Best C: %.5f' % param_C)
    else:
        best_model = model.fit(X_train, y_train)

    return best_model, param_C

def get_train_test(train_test_sets, fold, simple_features=True, train=True):
    records_train = train_test_sets['records_train']
    records_test = train_test_sets['records_test']

    articles_train = train_test_sets['articles_train']
    articles_test = train_test_sets['articles_test']

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

        X_train = myfeatures.combine(
            [X_train_ptf, X_train_stf, X_train_tf_idf, X_train_lda])
        X_test = myfeatures.combine(
            [X_test_ptf, X_test_stf, X_test_tf_idf, X_test_lda])

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

        train_test_sets = {}
        train_test_sets['records_train'] = [records[i] for i in list(i_train)]
        train_test_sets['records_test'] = [records[i] for i in list(i_test)]

        train_test_sets['articles_train'] = [articles[i] for i in list(i_train)]
        train_test_sets['articles_test'] = [articles[i] for i in list(i_test)]

        X_train, X_test = get_train_test(train_test_sets, fold, simple_features)

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
        draw_feature_importance(
                features=np.array(list(X_train.columns)),
                importance=np.array(model_coefs),
                fold=fold,
                simple_features=simple_features)

        ## interpretation
        # print('\nLR coefficients: ')
        # print([model_coefs[i] for i in range(len(model_coefs)) if features_mask[i]])

        ## predict
        y_probs = best_model.predict_proba(X_test)

        y_probs = y_probs[:, 1]
        draw_histogram(y_probs, fold, simple_features)

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
                    'wss': metrics['wss']},
                ignore_index=True)

    mean_performance(cfmat_overall)

    ## concatenate all probs and tests
    y_probs_all = np.concatenate(y_probs_all)
    y_test_all = np.concatenate(y_test_all)
    precision_all, recall_all, _ = precision_recall_curve(y_test_all, y_probs_all)

    ## save all probs for threshold selection histogram
    pd.DataFrame({'y': y_probs_all}).to_csv(r'../report/data/y_probs_all.csv', index=False)

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

    results = add_mean_performance(results)

    return results, plots


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == 'full':
        simple_features = False
        print('Evaluating the full model ...')
    else:
        simple_features = True
        print('Evaluating the simple model ...')

    results, plots = evaluate_model(simple_features=simple_features)

    show_performance(plots, simple_features)
    save_performance(plots, simple_features)

    print('\nEvaluation report: ')
    print(results.to_string(index=False))
