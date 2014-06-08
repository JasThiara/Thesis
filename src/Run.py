'''
Created on Nov 6, 2013

@author: Jas
'''
from sage.all import *
import csv, multiprocessing
from datetime import date
from FlorenZmirou import FlorenZmirou
from CrossValidation import *
def BuildNASDAQRowEntry(x):
    return FlorenZmirou(tickerParams=[x[0],1,60,False,x[1]])
def BuildNYSERowEntry(x):
    return FlorenZmirou(tickerParams=[x[0],1,60,True,x[1]])
'''
if __name__ == '__main__':
    L = ['GRPN',1,60,False,'goog inc']
    FZ = FlorenZmirou(tickerParams=L)
    FZ.CubicInterpolatedVariance.plot().save('%s_variance_spline.png'%L[0])
    FZ.CubicInterpolatedStandardDeviation.plot().save('%s_stdDev_spline.png'%L[0])
    list_plot(FZ.StockPrices).save('%s_stock_price.png'%L[0])
    list_plot(FZ.EstimatedStandardDeviation).save('%s_FZ_stddev_estimation.png'%L[0])
'''
if __name__ == '__main__':
    nasdaqFileReader = open('TickerSymbols/NASDAQ.csv','r')
    nasdaqFileWriter = open('TickerSymbols/bubbleOutput.csv','w')
    nasdaqCsvReader = csv.reader(nasdaqFileReader,delimiter=',')
    nasdaqCsvWriter = csv.writer(nasdaqFileWriter,delimiter=',')
    todaysDate = date.today()
    #fzList = [BuildNASDAQRowEntry(z) for z in nasdaqCsvReader]
    for z in nasdaqCsvReader:
        try:
            FZ = BuildNASDAQRowEntry(z)
            FZ.CubicInterpolatedVariance.plot().save('../gfx/%s_variance_spline.png'%z[0])
            FZ.CubicInterpolatedStandardDeviation.plot().save('../gfx/%s_stdDev_spline.png'%z[0])
            list_plot(FZ.StockPrices).save('../gfx/%s_stock_price.png'%z[0])
            list_plot(FZ.EstimatedStandardDeviation).save('../gfx/%s_FZ_stddev_estimation.png'%z[0])
            isBubble = FZ.InterpolationBubbleTest
            nasdaqCsvWriter.writerow((FZ.CompanyName,FZ.Ticker,todaysDate,isBubble,FZ.UsableGridPoints, min(FZ.StockPrice), max(FZ.StockPrice),))
        except:
            pass
    
