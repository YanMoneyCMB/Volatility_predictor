import pandas as pd
import numpy as np
import yfinance as yf
import math

def chartData(index, period, prediction):
    tick = yf.Ticker(index)
    data = tick.history(period=str(period)+'d').Close
    last_price = data.tail(1).values[0]
    maximum = last_price * (1+2*prediction)
    minimum = last_price * (1-2*prediction)
    return data, maximum, minimum


def getData(ticker, period):
    tick = yf.Ticker(ticker)
    raw = tick.history(start="2000-01-01")
    df = raw.reset_index().drop(columns=['Dividends','Stock Splits'])
    df.columns = [col.lower() for col in df.columns]
    tech = Technicals(df, period)
    return tech.calculate_technicals()

class Technicals:

    def __init__(self, data, period):

        self.data = data
        self.period = period
        self.close = data.close
        self.low = data.low
        self.high = data.high
        self.open = data.open
        self.returns = self.close.pct_change()
        self.data['return']=self.returns

    def RSI(self, n=14, average='Exponential'):

        '''
        Relative Strength Indicator

        Parameters
        ----------

        n: int
            Rolling window period (Default is 14)
        average: str
            Type of moving average (Exponential, Simple) (Default is Exponential)
        '''

        change = self.close.diff()

        up, down = change.copy(), change.copy()

        up[up < 0] = 0
        down[down > 0] = 0

        if average == 'Exponential':

            roll_up = up.ewm(span=n).mean()
            roll_down = down.abs().ewm(span=n).mean()

        elif average == 'Simple':

            roll_up = up.rolling(n).mean()
            roll_down = down.abs().rolling(n).mean()

        else:

            print('Incorrect average type specified')

        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))

        return RSI

    def ATR(self, n=14):

        '''
        Average True Range

        Parameters
        ----------

        n: int
            Rolling window period (Default is 14)
        '''

        TR_variants = pd.DataFrame()
        TR_variants["TR1"] = self.high.subtract(self.low)
        TR_variants["TR2"] = self.high.subtract(self.close).abs()
        TR_variants["TR3"] = self.low.subtract(self.close).abs()

        TR = TR_variants.max(axis=1)

        ATR = TR.rolling(n).mean()

        return ATR

    def CRTDR(self):
        '''
        Close Relative To Daily Range

        Parameters
        ________

        self

        '''
        self.data["CRTDR"] = np.where(self.data["open"] == self.data["high"], 0, (
                    (self.data["ATR"] - self.data["high"]) / (self.data["open"] - self.data['high'])))

    def EWMA(self, alpha=0.94):
        self.data["EWMA"] = self.data['return'].ewm(alpha=alpha).mean()

    def MACD(self, long=26, short=12):
        '''
        Moving Average Convergence Divergence, Buy/Sell signal

        Parameters
        ----------

        long:  int
            Length of the period of the signal line's EMA.
        short: int
            Length of the period of the MACD line's EMA.
        '''
        MACD = pd.DataFrame()
        MACD["long"] = self.close.ewm(span=long, adjust=False).mean()
        MACD["short"] = self.close.ewm(span=short, adjust=False).mean()
        MACD["indicator"] = MACD.short.subtract(MACD.long)

        MACD["signal"] = 0
        MACD.loc[(MACD["indicator"].shift() <= 0) & (MACD["indicator"] > 0), "signal"] = 1
        MACD.loc[(MACD["indicator"].shift() >= 0) & (MACD["indicator"] < 0), "signal"] = -1

        return MACD.indicator, MACD.signal

    def MACDRV(self):
        '''
        Moving Average Convergence Divergence of volatility

        Parameters
        ________

        self
        '''
        MACDRV = pd.DataFrame()
        MACDRV["long"] = self.data.hist_vol_28.ewm(span=28, adjust=False).mean()
        MACDRV["short"] = self.data.hist_vol_14.ewm(span=14, adjust=False).mean()
        MACDRV["indicator"] = MACDRV.short.subtract(MACDRV.long)

        return MACDRV.indicator

    def leverages(self, n=30):
        '''
        Leverage effects

        Parameters
        ----------

        n:  int
            Length of the rolling window.
        '''
        returns = self.returns
        pos_leverage = returns.rolling(window=n).agg(lambda x: (x > 0).sum()) / n
        neg_leverage = returns.rolling(window=n).agg(lambda x: (x < 0).sum()) / n
        return pos_leverage, neg_leverage

    def hist_vol(self, n):
        '''
        Calculate historical volatility over the past n days

        Parameters
        ___________

        n: int
            Length of the historical window
        '''
        self.data["hist_vol_" + str(n)] = self.data["return"].rolling(n).std()

    def williamsR(self):
        '''
        Williams R%

        Parameters
        ----------

        N/A
        '''
        williams = (self.high.shift(1).rolling(14).max() - self.close.shift(1)) / (
                    self.high.shift(1).rolling(14).max() - self.low.shift(1).rolling(14).min())
        return williams

    def bollingerband(self, period=10):
        '''
        Bollinger Bands

        Parameters
        ----------

        period: int
                length of the observation period
        '''

        df = pd.DataFrame()
        df['MA'] = self.close.ewm(span=period, adjust=False).mean()
        df['STD'] = self.close.ewm(span=period, adjust=False).std()
        df['BollingerUp'] = df['MA'] + df['STD']
        df['BollingerDn'] = df['MA'] - df['STD']
        df['BolUpInd'] = (self.close > df['BollingerUp']) ** 1
        df['BolDnInd'] = (self.close < df['BollingerDn']) ** 1
        return df['BollingerUp'], df['BollingerDn'], df['BolUpInd'], df['BolDnInd']

    def aroon(self, period=25):
        '''
        Aroon indicator

        Parameters
        ----------

        period: int
                length of the observation period
        '''
        df = pd.DataFrame()
        df['Max 25'] = self.close.rolling(period).max()
        df['Min 25'] = self.close.rolling(period).min()
        df['Periods since Max'] = df.groupby((df['Max 25'] != df['Max 25'].shift(1)).cumsum()).cumcount()
        df['Periods since Min'] = df.groupby((df['Min 25'] != df['Min 25'].shift(1)).cumsum()).cumcount()
        df['AroonUp'] = 100 * ((period - df['Periods since Max']) / period)
        df['AroonDn'] = 100 * ((period - df['Periods since Min']) / period)
        return df['AroonUp'], df['AroonDn']

    def trix(self):
        '''
        Trix

        Parameters
        ----------

        N/A

        '''
        df = pd.DataFrame()
        df['ema1'] = self.close.ewm(alpha=2 / (9 + 1), adjust=False).mean()
        df['ema2'] = df['ema1'].ewm(alpha=2 / (9 + 1), adjust=False).mean()
        df['ema3'] = df['ema2'].ewm(alpha=2 / (9 + 1), adjust=False).mean()
        df['trix'] = (df['ema3'] - df['ema3'].shift(1)) / df['ema3'].shift(1)
        return df['trix']

    def calculate_technicals(self):
        '''
        Calculate technical indicators

        Parameters
        ----------

        N/A

        '''

        self.data["RSI"] = self.RSI(self.period)
        self.data["ATR"] = self.ATR(self.period)
        self.CRTDR()
        self.EWMA()
        self.hist_vol(5)
        self.hist_vol(10)
        self.hist_vol(14)
        self.hist_vol(28)
        self.data["MACD"], self.data["MACD_sig"] = self.MACD()
        self.data["Positive_lev"], self.data["Negative_lev"] = self.leverages(self.period)
        self.data["MACDRV"] = self.MACDRV()
        self.data["WilliamsR"] = self.williamsR()
        self.data['BollingerUp'], self.data['BollingerDn'], self.data['BolUpInd'], self.data[
            'BolDnInd'] = self.bollingerband(self.period)
        self.data['AroonUp'], self.data['AroonDn'] = self.aroon(self.period)
        self.data["TRIX"] = self.trix()
        return self.data.dropna()



