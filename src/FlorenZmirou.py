'''
Created on Oct 27, 2013

@author: Jas
'''
from sage.all import *
from Stock import Stock
from EulerMaruyama import EulerMaruyama
from Spline import NaturalCubicSpline
import locale
import sys
class FlorenZmirou(Stock,EulerMaruyama):
    '''
    FlorenZmirou will provide us list of sigma values and interpolation from list of stock prices
    '''
    def GetGridPoints(self):
        '''
        Description: It will make grid Points
        Output: Returns list of grid points
        '''
        self.n = len(self.StockPrices)
        self.h_n = self.Derive_hn(self.StockPrices)
        self.T = 60*self.n # 60 sec times total number of data points because T is every minute from [0,T]
        return self.Derive_x_values(self.StockPrices)
    
    
    def __init__(self,**kwds):
        '''
        Input:
        Keyword Usage:
        if filename is used, it will read the yahoo API based minute to minute data:
        
        Stock(filename="Filename.csv")
        
        - or -
        
        if tickerParams is used, it will use the google API to retrieve minute to minute data
        
        Stock(tickerParams=['appl',10,60,False])
        where 
        Input
        Parameters = [ticker,days,period,isNYSE,companyName]
        1)the first element in the list is a string of the ticker symbol, e.g. 'appl'
        2)the second element in the list is the historical data period, e.g. 10 days
        3)the third element in the list is the period of data in seconds, e.g. 60 (seconds)
        4)the fourth element in the list is True or False.  True -> ticker is on NYSE, False -> ticker is on NASDAQ
        5)the fifth element in the list is the company name as a string
        Description: Step1: From stock, it will give us sigma(x)
                     Step2: Interpolate sigma(x) using step1.
        '''
        if 'tickerParams' in kwds:
            Stock.__init__(self,tickerParams=kwds)
        elif 'filename' in kwds:
            Stock.__init__(self,filename=kwds)
        elif 'en' in kwds:
            EulerMaruyama.__init__(self,kwds['en'])
        if not hasattr(self,'StockPrices'):
            pass
        else:
            if len(self.StockPrices) > 30 :
                self.GridPoints = self.GetGridPoints()
                self.UsableGridPoints, self.StockPricesByGridPointDictionary = self.DoGridAnalysis(self.T,self.StockPrices,self.GridPoints,self.n,self.h_n,.05)
                if len(self.UsableGridPoints) >= 3:
                    self.EstimatedVariance = [self.Volatility_estimation(self.T,self.StockPrices,ex,self.n,self.h_n)**2 for ex in self.StockPrices]# these are the sigma values evulated at the grid points
                    self.PriceEstimatedVarianceDictionary = {ex:self.Volatility_estimation(self.T,self.StockPrices,ex,self.n,self.h_n)**2 for ex in self.StockPrices} 
                    self.CreateZmirouTable()
                    self.EstimatedStandardDeviation = [i**(1.0/2.0) for i in self.EstimatedVariance]
                    self.InverseVariance = [1.0/i for i in self.EstimatedVariance]
                    self.InverseStandardDeviation = [1.0/i for i in self.EstimatedStandardDeviation]
                    self.CubicInterpolatedVariance = self.GetCubicInterpolatedVariance()
                    self.CubicInterpolatedStandardDeviation = self.GetCubicSplineInterpolatedStandardDeviation()
                    self.GridVariance = self.GetGridVariance()
                    self.InterpolatedRange = (self.minPrice,self.maxPrice)
                    self.InterpolationBubbleTestResult = self.InterpolationBubbleTest(self.EstimatedVariance, self.StockPrices)
                    self.InterpolationBubbleTest = self.InterpolationBubbleTestResult <= 0  #if true, the not a bubble.  if false, then perhaps a bubble.
        
    def InterpolationBubbleTest(self, EV, SP):
        '''
        Description:
            Test 1: Test the slope of the floren-Zmirou volatility estimator
            Test procedure:
                1)  Calculate the numerical estimation of the derivative
                2)  Calculate numerical estimate of mean value theorem.
        input:
            Estimated Variance     - EV
            Stock Prices           - SP
        output:
                            1      |\ b
            sigma'(c) =   -----    |      sigma'(x) dx
                          b - a   \|  a
        '''
        #self.EstimatedVariance = [self.Volatility_estimation(self.T,self.StockPrices,ex,self.n,self.h_n)**2 for ex in self.StockPrices]# these are the sigma values evulated at the grid points
        xValues = SP
        yValues = EV
        derivative = [ (yValues[i] - yValues[i+1])/(xValues[i] - xValues[i+1]) for i in range(len(yValues)-1) if xValues[i] - xValues[i+1] != 0.0]
        b = max(xValues)
        a = min(xValues)
        xCount = len(xValues)
        h = (b-a)/(xCount-1.0)  #1 less value to evaluate for derivative
        derivativeSum = sum(derivative)
        integralValue = h * derivativeSum
        meanValueTheorem = (1/(b-a)) * integralValue
        return meanValueTheorem
        
        
    def GetGridInverseStandardDeviation(self):
        '''
        Description:
        Gets floren zmirou estimation over usable grid points
        '''
        Points = []
        half_x_hn = self.x_step_size(self.StockPrices)/2.0
        for x in self.StockPricesByGridPointDictionary.iterkeys():
            y = 1/self.Volatility_estimation(self.T,self.StockPrices,x,self.n,half_x_hn)**2
            Points.append((x,y))
        return Points
    def GetGridVariance(self):
        '''
        Description:
        Gets floren zmirou estimation over usable grid points
        '''
        Points = []
        half_x_hn = self.x_step_size(self.StockPrices)/2.0
        for x in self.StockPricesByGridPointDictionary.iterkeys():
            y = self.Volatility_estimation(self.T,self.StockPrices,x,self.n,half_x_hn)**2 
            Points.append((x,y))
        return Points
    def GetGridSigma(self):
        Points = []
        half_x_hn = self.x_step_size(self.StockPrices)/2.0
        for x in self.StockPricesByGridPointDictionary.iterkeys():
            y = self.Volatility_estimation(self.T,self.StockPrices,x,self.n,half_x_hn)
            Points.append((x,y))
        return Points
    
    def GetCubicInterpolatedVariance(self):
        '''
        Description: It will give us cubic spline interpolation of sigma squared of grid points.
        Output: Given a list of grid points and estimated sigma squared, spline(Points) is an object such that spline(Points) is the value of the spline interpolation through the points in grid points and estimated sigma squared
        '''
        Points = self.GetGridVariance()
        return NaturalCubicSpline(Points)

    def GetCubicSplineInterpolatedStandardDeviation(self):
    	'''
    	Description: creates a cubic spline interpolation of sigma by the grid points.
    	Output: give a list of grid points and estimated sigma, spline(Points) is an object such that it is the value of the cubic spline interpolation through the points in grid points and estimated sigma
    	'''
        Points = self.GetGridSigma()
        return NaturalCubicSpline(Points)

    def Sublocal_Time(self,T,S,x,n,h_n):
        """
        funtion: Sublocal_time
        input:T is time period 
              1) stock price (s(t1).......s(tn))= S
              2) x values in [0,infinity)
              3) n , h_n
        outout L_T^n(x)
        
        Description: L_T^n(x) = (T/ 2nh_n) sigma i =1,n 1_{|s_t(i)-x)| < h_n}
    
        """
        sum = 0.0
        scalar = T/(2.0*n*h_n)
        for i in range(len(S)):
            Sti = S[i]
            absoluteValue = abs(Sti-x)
            indicatorValue = self.Indicator_function(absoluteValue<h_n)
            sum = sum+indicatorValue
        return scalar*sum
          
            
    def Local_time(self,T,S,x,n,h_n):
        """
        funtion: Local_time
        input:
              1) stock price (s(t1).......s(tn))= S
              2) x values in [0,infinity)
              3) n , h_n
        outout l_T^n(x) = l_T^n(x)*S_n(x)
        
        Description: l_T^n(x) = (T/ 2nh_n) sigma i =1,n-1 1_{|s_t(i)-x)| < h_n}*n(s(t(i+1))-s(t(i))^2
        """
        sum = 0.0
        scalar = T/(2.0*n*h_n)
        for i in range(len(S)-1):
            Sti = S[i]
            Stj = S[i+1]
            absoluteValue = abs(Sti-x)
            Difference = (Stj-Sti)**2
            indicatorValue = self.Indicator_function(absoluteValue<h_n)
            sum = sum+indicatorValue*n*Difference
        return scalar*sum
    
    def Volatility_estimation(self,T,S,x,n,h_n):
        """
        funtion: Volatility_estimator
        input:
              1) stock price (s(t1).......s(tn))= S
              2) x values in [0,infinity)
              3) n , h_n
        outout l_T^n(x) = (l_T^n(x)*S_n(x))/(sigma i =1,n-1 1_{|s_t(i)-x)| < h_n})
        
        Description: S_n(x) = (l_T^n(x))/(sigma i =1,n-1 1_{|s_t(i)-x)| < h_n})
        """
        localTime = self.Local_time(T,S,x,n,h_n)
        sublocalTime = self.Sublocal_Time(T,S,x,n,h_n)
        ratio = localTime/sublocalTime
        return ratio
    
    def Indicator_function(self,condition):
        """
        function Indicator_function
        input:
             condition
        output:
              0 or 1
              
        Description : (sigma i =1,n-1 1_{|S(s)-x)| < h_n})
        """
        return condition
    
    def Derive_hn(self,S):
        """
        Derive h_n function
        input:
               stock price (s(t1).......s(tn))= S
        outout h_n
        
        Description: 1/n^(1/3)
        """
        n = len(S)
        h_n = 1.0/n**(1.0/3.0)
        return h_n
    
    def x_step_size(self,S):
        """
        Derive x values function
        input:
               stock price (s(t1).......s(tn))= S
        outout x grid points
        Description: trying to create step size to generate x
        """
        h_n = self.Derive_hn(S)
        doubleh_n = 2.0*h_n
        Difference= max(S)-min(S)
        x_hn =Difference*doubleh_n
        return x_hn
    
    def Derive_x_values(self,S):
        """
     
        input:
               stock price (string as file location pythons(t1).......s(tn))= S
        outout x values
        Description: Derive x grid points
        """
        x_hn = self.x_step_size(S)
        halfh_n = x_hn/2.0
        x = list()
        x.append(min(S)+halfh_n)
        ex = x[0]
        Smax = max(S)
        while ex <Smax:
            ex = ex+x_hn
            x.append(ex)
        return x

    def DoGridAnalysis(self,T,S,x,n,h_n,Y):
        '''
        Input:1) T = Time from[0,T] which is for a day each mintue (60*n)
             2) S = Stock prices
             3) x = Grid Points
             4) h_n = 1/n^(1/3)
             5) n = Number of stock data points
             6) Y =  Y percent of total data points
        Ingredients: 1) S_(ti), 
                     2) indicator function, 
                     3) grid points, 
                     4) a dictionary where the keys are the grid points and the value is a list for each grid point (used in Step 2)
        Description : sigma i =1,n-1 1_{|s_t(i)-x)| < h_n} = *
        Recipe:           step1: 
                              for Si in S1,S2....Sn:
                                   for x in X1,X2...Xm:
                                      if |Si-x|<x_hn:
                                        step 2: 
                                        Add Si into list corresponding to x
                               Step 3:
                               for x in X1, X2,...,Xm: 
                                    if the list of data points corresponding to x has greater than Y% of total grid points n:
                                         add it to the list of usable grid points
                               Step 4:
                               return the outputs
        Output: 1) the list of usable grid points
                   2) for each usable grid point, the list of stockprices
            n=len(S)
        '''
        usableGridPoints = x
        d = dict()# Creating empty dictionary
        x_hn = self.x_step_size(S)
        halfh_n = x_hn/2.0
        stockPriceCount = float(len(S)) 
        for gridPoint in x:# The grid points are your keys
            d[gridPoint]=list()#a dictionary where the keys are the grid points and the value is a list for each grid point (used in Step 2)
            for stockPrice in S:# stock price in S    
                if  abs(gridPoint-stockPrice)<halfh_n:# satisfying the condition if true then add x value to corresponding Si
                    d[gridPoint].append(stockPrice)#Note the number of points for the gridPoint is len(d[gridPoint])
            numberOfPointsInList = float(len(d[gridPoint]))
            percentOfStockPrices = numberOfPointsInList / float(stockPriceCount)
            if  percentOfStockPrices < Y:# We just want to remove the number grid points from the dictionary since we have all data.
                usableGridPoints.remove(gridPoint)
                d.pop(gridPoint,None)
                #del d[gridPoint]#pop(key[, default]) If key is in the dictionary, remove it and return its value, else return default. If default is not given and key is not in the dictionary, a KeyError is raised.
        return usableGridPoints, d# 1) the list of usable grid points 2) for each usable grid point, the list of usable grid points

    def format_num(self,num):
        """
        Format a number according to given places.
        Adds commas, etc. Will truncate floats into ints!
        """
        try:
            inum = int(num)
            return locale.format("%.*f", (0, inum), True)
    
        except (ValueError, TypeError):
            return str(num)
        
    def get_max_width(self,table, index):
        """Get the maximum width of the given column index"""
        return max([len(self.format_num(row[index])) for row in table])
    
    def pprint_table(self,out, table):
        """Prints out a table of data, padded for alignment
        @param out: Output stream (file-like object)
        @param table: The table to print. A list of lists.
        Each row must have the same number of columns. 
        """
        col_paddings = []
        for i in range(len(table[0])):
            col_paddings.append(self.get_max_width(table, i))
        for row in table:
            # left col
            print >> out, row[0].ljust(col_paddings[0] + 1),
            # rest of the cols
            for i in range(1, len(row)):
                col = self.format_num(row[i]).rjust(col_paddings[i] + 2)
                print >> out, col,
            print >> out
            
    def CreateZmirouTable(self):
        '''
        #1.3) create table with the following:
        #1.3.1) Usable Grid Points
        #1.3.2) Estimated Sigma value from Floren Zmirou Estimator
        #1.3.3) Number of Points for each Grid Point
        '''
        table= []
        columnNames = ["Usable Grid Points", "Estimated Sigma Zmirou", "Number of Points"]
        table.append(columnNames)
        gridPoints = self.UsableGridPoints
        estimatedSigma = self.EstimatedVariance
        #for i in range(len(gridPoints)):i
        for gridPoint,StockPrices in self.StockPricesByGridPointDictionary.iteritems(): 
            table.append([str(gridPoint), str(self.Volatility_estimation(self.T,self.StockPrices,gridPoint,self.n,self.x_step_size(self.StockPrices)/2.0)**2), str(len(StockPrices))])
        out = sys.stdout
        return self.pprint_table(out, table)
