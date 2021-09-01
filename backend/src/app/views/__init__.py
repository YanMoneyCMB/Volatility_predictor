from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from .dataGetter import getData, chartData
from .modelTrainer import trainer

yahoo_mapping = {"DJIA":"^DJI", "SPX":"^GSPC","IXIC":"^IXIC","XAX":"^XAX","RUT":"^RUT", "UKX":"^FTSE",
                 "DAX":"^GDAXI","NIK2":"^N225", "LFG9": "^DJSH","ESTX":"^STOXX50E"}
class Predict(Resource):
    def get(self, index, period):
        yahoo_ticker = yahoo_mapping[index]
        df = getData(yahoo_ticker, period)
        to_predict = df.tail(1)
        dir_model, final_model = trainer(df,index,period)
        to_predict['Dir'] = dir_model.predict(to_predict.drop(columns=['date','hist_vol_5',
                                                                       'hist_vol_14','hist_vol_28','Positive_lev','Negative_lev']))
        vol = final_model.predict(to_predict[['return','hist_vol_5','hist_vol_14','hist_vol_28','Positive_lev','Negative_lev','Dir']])
        print(vol)
        return jsonify(vol[0])

class Project(Resource):
    def get(self, index, period, prediction):
        data,minimum,maximum = chartData(yahoo_mapping[index],period,prediction)

        return jsonify(data = data.values.tolist(),dates=data.index.strftime("%d-%m-%Y").values.tolist(), minimum=minimum, maximum=maximum)



