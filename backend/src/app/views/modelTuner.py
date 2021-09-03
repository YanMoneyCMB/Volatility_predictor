import pandas as pd
from pandas.api.indexers import FixedForwardWindowIndexer
import numpy as np
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn import metrics as score
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
import pickle as pickle
import math

def tune_regression(data,ticker,period):
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start=50, stop=2000, num=20)]
    # Number of features to consider at every split
    max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]
    # Create the random grid
    grid = {'n_estimators': n_estimators,
                 'max_features': max_features,
                 'max_depth': max_depth,
                 'min_samples_split': min_samples_split,
                 'min_samples_leaf': min_samples_leaf,
                 'bootstrap': bootstrap}



    data = data.reset_index().drop(columns=['Date']).dropna()
    pickle_off = open("./app/views/storage/RF_dir_hyperparameters.pkl", "rb")
    dir_hyperparameters = pickle.load(pickle_off)
    data = reg_targets(data,period)
    hyperparam = dir_hyperparameters["dir_" + str(period) + "_" + ticker]
    direction_model = RandomForestClassifier()
    direction_model.set_params(**hyperparam)
    X, y = data.drop(columns=['Target', 'Target_vol', 'hist_vol_5', 'hist_vol_10',
                                 'hist_vol_14', 'hist_vol_28', 'date']), data.Target
    direction_model.fit(X, y)
    data['Direction'] = direction_model.predict(X)

    X = data.drop(columns=['RSI', 'ATR', 'CRTDR', 'EWMA', 'MACD',
                              'MACD_sig', 'MACDRV', 'WilliamsR', 'BollingerUp', 'BollingerDn',
                              'BolUpInd', 'BolDnInd', 'AroonUp', 'AroonDn', 'TRIX', 'Target',
                              'Target_vol', 'date'])
    y = data['Target_vol']

    tscv = TimeSeriesSplit(3)
    rf = RandomForestRegressor()
    rf_grid = RandomizedSearchCV(estimator=rf,
                                 param_distributions=grid,
                                 n_jobs=-1,
                                 n_iter=1,
                                 cv=tscv,
                                 verbose=3)
    model = rf_grid.fit(X, y)
    hyperparam = model.best_estimator_.get_params()

    pickle_off = open("./app/views/storage/RF_mag_hyperparameters.pkl", "rb")
    mag_hyperparameters = pickle.load(pickle_off)
    mag_hyperparameters['reg_' + str(period) + '_' + ticker] = hyperparam
    with open('./app/views/storage/RF_mag_hyperparameters.pkl', 'wb') as handle:
        pickle.dump(dir_hyperparameters, handle)






def reg_targets(data,period):
    df = data
    indexer = FixedForwardWindowIndexer(window_size=period)
    df['Target_vol'] = df['return'].rolling(indexer).std()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna()
    df['Target'] = np.where(df['Target_vol'] > df['hist_vol_' + str(period)], 1, -1)
    return df

def tune_direction(data,ticker,period):
    data = data.reset_index().drop(columns=['date']).dropna()
    depth = [int(x) for x in np.linspace(30, 110, num=10)]
    depth.append(None)
    grid = {'n_estimators': [int(x) for x in np.linspace(start=1000, stop=2000, num=100)],
             'max_features': ['auto', 'sqrt'],
             'max_depth': depth,
             'min_samples_split': [2, 5, 10],
             'min_samples_leaf': [1, 2, 4],
             'bootstrap': [True, False]}
    data = dir_targets(data,period)
    X = data.drop(columns=['Target'])
    y = data['Target']

    tscv = TimeSeriesSplit(3)
    rf = RandomForestClassifier()
    rf_grid = RandomizedSearchCV(estimator=rf,
                                 param_distributions=grid,
                                 n_jobs=-1,
                                 n_iter=1,
                                 cv=tscv,
                                 verbose=3)
    model = rf_grid.fit(X, y)
    params = model.best_estimator_.get_params()
    pickle_off = open("./app/views/storage/RF_dir_hyperparameters.pkl", "rb")
    dir_hyperparameters = pickle.load(pickle_off)
    dir_hyperparameters['dir_'+str(period)+'_'+ticker] = params
    with open('./app/views/storage/RF_dir_hyperparameters.pkl', 'wb') as handle:
        pickle.dump(dir_hyperparameters, handle)



def dir_targets(data,period):
    df = data
    indexer = FixedForwardWindowIndexer(window_size=period)
    df['Target_vol'] = df['return'].rolling(indexer).std()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df = df.dropna()
    df['Target'] = np.where(df['Target_vol'] > df['hist_vol_' + str(period)], 1, -1)
    df = df.drop(columns=['Target_vol'])
    return df