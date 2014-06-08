'''
Created on Nov 6, 2013

@author: Jas
'''
from sage.all import *
import csv, multiprocessing
from datetime import date
from FlorenZmirou import FlorenZmirou
def BuildNASDAQRowEntry(x):
    return FlorenZmirou(tickerParams=[x[0],1,60,False,x[1]])
def BuildNYSERowEntry(x):
    return FlorenZmirou(tickerParams=[x[0],1,60,True,x[1]])
def LoopInstructions(csvWriter,BuildRowEntry,z):
    try:
        FZ = BuildRowEntry(z)
        FZ.CubicInterpolatedVariance.plot().save('../gfx/%s_%s_variance_spline.png'%(z[0],todaysDate.strftime('%Y%m%d')))
        FZ.CubicInterpolatedStandardDeviation.plot().save('../gfx/%s_%s_stdDev_spline.png'%(z[0],todaysDate.strftime('%Y%m%d')))
        list_plot(FZ.StockPrices).save('../gfx/%s_%s_stock_price.png'%(z[0],todaysDate.strftime('%Y%m%d')))
        list_plot(FZ.EstimatedStandardDeviation).save('../gfx/%s_%s_FZ_stddev_estimation.png'%(z[0],todaysDate.strftime('%Y%m%d')))
        isBubbleFZ = FZ.InterpolationBubbleTestValue
#        isBubbleSpline = FZ.SplineBubbleTestValue
        csvWriter.writerow((FZ.CompanyName,FZ.Ticker,todaysDate,isBubbleFZ,FZ.UsableGridPoints, min(FZ.StockPrice), max(FZ.StockPrice)))
    except:
        pass
if __name__ == '__main__':
    nasdaqFileReader = open('NASDAQ.csv','r')
    nyseFileReader   = open('NYSE.csv','r')
    fileWriter       = open('bubbleOutput.csv','w')
    nasdaqCsvReader  = csv.reader(nasdaqFileReader, delimiter=',')
    nyseCsvReader    = csv.reader(nyseFileReader,   delimiter=',')
    CsvWriter  = csv.writer(fileWriter,       delimiter=',')
    todaysDate       = date.today()
    CsvWriter.writerow(('Company Name','Ticker Symbol','Date','Is Bubble Detected? (FZ)','Usable Grid Points', 'Minimum Stock Price', 'Maximum Stock Price'))
    for z in nasdaqCsvReader:
        LoopInstructions(CsvWriter,BuildNASDAQRowEntry,z)
    for z in nyseCsvReader:
        LoopInstructions(CsvWriter,BuildNYSERowEntry,z)