""" Custom Indicator Increase In  Volume
"""

from scipy import stats
from talib import abstract
import numpy as np
import pandas

from analyzers.utils import IndicatorUtils


class MARibbon(IndicatorUtils):

    #Exponential Moving Average
    def EMA(self, df, n, field = 'close'):
        return pandas.Series(abstract.EMA(df[field].astype('f8').values, n), name = 'EMA_' + field.upper() + '_' + str(n), index = df.index)

    def MA_RIBBON(self, df, ma_series):
        ma_array = np.zeros([len(df), len(ma_series)])
        ema_list = []
        for idx, ma_len in enumerate(ma_series):
            ema_i = self.EMA(df, n = ma_len, field = 'close')
            ma_array[:, idx] = ema_i
            ema_list.append(ema_i)
        corr = np.empty([len(df)])
        pval = np.empty([len(df)])
        dist = np.empty([len(df)])
        corr[:] = np.NAN
        pval[:] = np.NAN
        dist[:] = np.NAN
        max_n = max(ma_series)
        
        for idy in range(len(df)):
            if idy >= max_n - 1:
                corr[idy], pval[idy] = stats.spearmanr(ma_array[idy,:], range(len(ma_series), 0, -1))
                dist[idy] = max(ma_array[idy,:]) - min(ma_array[idy,:])
        
        corr_ts = pandas.Series(corr*100, index = df.index, name = "MARIBBON_CORR")
        pval_ts = pandas.Series(pval*100, index = df.index, name = "MARIBBON_PVAL")
        dist_ts = pandas.Series(dist, index = df.index, name = "MARIBBON_DIST")
        
        return pandas.concat([corr_ts, pval_ts, dist_ts] + ema_list, join='outer', axis=1)

    def analyze(self, historical_data, signal=['ma_ribbon'], hot_thresh=10, cold_thresh=0):
        """Performs an analysis about the increase in volumen on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            signal (list, optional): Defaults to ma_ribbon. The indicator line to check hot against.
            hot_thresh (float, optional): Defaults to 10. 
            cold_thresh: Unused
            

        Returns:
            pandas.DataFrame: A dataframe containing the indicator and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        
        ma_series = [5, 15, 25, 35, 45]

        ma_ribbon = self.MA_RIBBON(dataframe, ma_series)


        """
        z = np.abs(stats.zscore(dataframe['volume']))
        filtered = dataframe.volume[(z < 3)]
        
        previous_mean = filtered.mean()
        
        dataframe[signal[0]] = dataframe['volume'] / previous_mean

        dataframe['is_hot']  = dataframe[signal[0]] >= hot_thresh
        dataframe['is_cold'] = False
        """

        return dataframe