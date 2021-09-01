from flask_restful import Resource, Api, reqparse
import pandas as pd
from pandas.api.indexers import FixedForwardWindowIndexer
import numpy as np
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn import metrics as score
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
import pickle as pickle
import math
from tqdm import tqdm_notebook as tqdm
import os

def trainer(data,ticker, period):
    print(os.getcwd())
    pickle_off = open("./app/views/storage/RF_dir_hyperparameters.pkl","rb")
    dir_hyperparameters= pickle.load(pickle_off)
    pickle_off = open("./app/views/storage/RF_mag_hyperparameters.pkl","rb")
    mag_hyperparameters= pickle.load(pickle_off)
    indexer = FixedForwardWindowIndexer(window_size=period)
    data['Target_vol'] = data['return'].rolling(indexer).std()
    data['Dir'] = np.where(data['Target_vol'] > data['hist_vol_' + str(period)], 1, -1)
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data = data.dropna()
    dir_param = dir_hyperparameters['dir_'+str(period)+'_'+ticker]
    mag_param = mag_hyperparameters['reg_' + str(period) + '_' + ticker]
    dir_model = RandomForestClassifier()
    dir_model.set_params(**dir_param)
    dir_model.fit(data.drop(columns=['Target_vol', 'date','hist_vol_5','hist_vol_14','hist_vol_28','Positive_lev','Negative_lev','Dir']),
                  data.Dir)
    data['Dir'] = dir_model.predict(data.drop(columns=['Target_vol', 'date','hist_vol_5','hist_vol_14','hist_vol_28','Positive_lev','Negative_lev','Dir']))

    final_model = RandomForestRegressor()
    final_model.set_params(**mag_param)
    final_model.fit(data[['return','hist_vol_5','hist_vol_14','hist_vol_28','Positive_lev','Negative_lev','Dir']],data.Target_vol)
    return dir_model, final_model