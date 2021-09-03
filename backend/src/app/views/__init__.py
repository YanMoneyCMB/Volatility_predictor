from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from .dataGetter import getData, chartData,getOptions
from .modelTrainer import trainer
from .modelTuner import tune_regression,tune_direction

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

        return jsonify(data = data.values.tolist(),dates=data.index.strftime("%d-%m-%Y").values.tolist().append("+"+str(period)+" days"), minimum=minimum, maximum=maximum)

class Options(Resource):

    def get(self, index, period):
        options, date = getOptions(yahoo_mapping[index],period)
        if options == False:
            return jsonify(resp = False)
        else:
            print("sending options over!!!!")
            return jsonify(resp = "True", calls = options.calls.drop(columns=['contractSymbol', 'lastTradeDate','bid', 'ask', 'openInterest','percentChange','contractSize', 'currency','volume','change']).to_json(orient="records"),
                           puts = options.puts.drop(columns=['contractSymbol', 'lastTradeDate','bid', 'ask', 'openInterest','contractSize','percentChange', 'currency','volume','change']).to_json(orient="records"),
                           date = date, columns=options.puts.drop(columns=['contractSymbol', 'lastTradeDate','bid', 'ask', 'openInterest','percentChange','contractSize', 'currency','volume','change']).columns.values.tolist())

class Tune(Resource):
    def get(self):
        for ticker in yahoo_mapping.keys():
            for period in [5,14,28]:
                yahoo_ticker = yahoo_mapping[ticker]
                print(ticker, period)
                df = getData(yahoo_ticker, period)
                tune_direction(df,ticker,period)
        for ticker in yahoo_mapping.keys():
            for period in [5,14,28]:
                yahoo_ticker = yahoo_mapping[ticker]
                df = getData(yahoo_ticker, period)
                tune_regression(df,ticker,period)







