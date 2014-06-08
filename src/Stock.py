'''
Created on Oct 27, 2013

@author: Jas
'''
import csv
import urllib 
import time
class Stock:
    '''
    Stock class will read a csv file provide a list of stock prices 
    '''
    def GetMaxStockPrice(self):
        '''
        Output Description: returns the largest recorded StockPrice
        '''
        return max(self.StockPrices)
    def GetMinStockPrice(self):
        '''
        Output Description: returns the smallest recorded StockPrice
        '''
        return min(self.StockPrices)
    def IsNumber(self,rowValue):
        ''' Output Description: Determine if rows of stock data is a numerical string or not.'''
        try:
            float(rowValue)
            return True
        except ValueError:
            return False
    def GetGoogleData(self,Parameters):
        '''
        Input
        Parameters = [ticker,days,period,isNYSE,CompanyName]
        1)the first element in the list is a string of the ticker symbol, e.g. 'appl'
        2)the second element in the list is the historical data period, e.g. 10 days
        3)the third element in the list is the period of data in seconds, e.g. 60 (seconds)
        4)the fourth element in the list is True or False.  True -> ticker is on NYSE, False -> ticker is on NASDAQ
        5)the fifth element in the list is the company name as a string
        '''
        stockPrices = []
        if Parameters['tickerParams'][3]:
            exchange = 'NYSE'
        else:
            exchange = 'NASD'
        currentTime = int(time.time())
        link = 'http://www.google.com/finance/getprices?q=%s&x=%s&i=%d&p=%dd&f=d,c,o,h,l&df=cpct&auto=1&ts=%d'%(Parameters['tickerParams'][0].upper(),exchange,Parameters['tickerParams'][2],Parameters['tickerParams'][1],currentTime)
        # q = ticker, x = exchange, i = 60 seconds, p = days 
        # link = 'http://www.google.com/finance/getprices?i=%d&p=%dd&f=d,o,h,l,c,v&df=cpct&q=%s&x=%s'%(Parameters[2],Parameters[1],Parameters[0],exchange)
        try:
            filePtr = urllib.urlopen(link)
            DataList = filePtr.readlines()
            tickerData = DataList[7:len(DataList)]
            for minuteData in tickerData:
                datum = minuteData.split(',')
                stockPrices.append(float(datum[1]))
        except:
            pass
        return stockPrices
        
    def __init__(self,**kwds):
        '''
        Keyword Usage:
        if filename is used, it will read the yahoo API based minute to minute data:
        
        Stock(filename="Filename.csv")
        
        - or -
        
        if tickerParams is used, it will use the google API to retrieve minute to minute data
        
        Stock(tickerParams=[ticker,days,period,isNYSE,CompanyName])
        where 
        1)the first element in the list is a string of the ticker symbol, e.g. 'appl'
        2)the second element in the list is the historical data period, e.g. 10 days
        3)the third element in the list is the period of data in seconds, e.g. 60 (seconds)
        4)the fourth element in the list is True or False.  True -> ticker is on NYSE, False -> ticker is on NASDAQ
        5)the fifth element in the list is the company name as a string
        Description: it will give us list of stock prices from csv file.
        ''' 
        if 'filename' in kwds:
            self.StockPrices=self.GetStockPrices(kwds['filename'])
        elif 'tickerParams' in kwds:
            self.StockPrices=self.GetGoogleData(kwds['tickerParams'])
            self.Ticker = kwds['tickerParams']['tickerParams'][0]
            self.CompanyName = kwds['tickerParams']['tickerParams'][4]
        else:
            raise Exception("bad paramaters")
        self.maxPrice = self.GetMaxStockPrice()
        self.minPrice = self.GetMinStockPrice()
        
        
    def GetStockPrices(self,FileName): 
        '''
        Input: FileName
        Description: Getting stock prices for that FileName
        Output: list of Stock prices
        ''' 
        cr = csv.reader(open(FileName,"r U"))
        next(cr, None) # skip the header
        c1 = []
        for row in cr: # reading file from csv file    
            if self.IsNumber(row[1]):#if the string, row[1], is a numerical string 
                c1.append(float(row[1]))#add it into the list
        return c1