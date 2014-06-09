r"""
Implements the Natural Cubic Spline from Numerical Analysis 8th ed. Burden & Faires

The natural cubic spline is a piecewise cubic polynomial spline interpolation.
Given a function f defined on [a,b] and a set of nodes a=x0 < x1 < ... < xn=b
a natural cubic spline interpolant S for f is a function that satisfies the
the following conditions:
(a) S(x) is a cubic polynomial, denoted S_j(x), on the subinterval 
	[x_j, x_{j+1}] for each j=0,1,...,n-1
(b) S_j(x_j) = f(x_j) and S_j(x_{j+1}) = f(x_{j+1}) for each j=0,1,...,n-1
(c) S_{j+1}(x_{j+1}) = S_j(x_{j+1}) for each j = 0,1,...,n-2
(d) S_{j+1}'(x_{j+1}) = S_j'(x_{j+1}) for each j = 0,1,...,n-2
(e) S_{j+1}''(x_{j+1}) = S_j''(x_{j+1}) for each j = 0,1,...,n-2
(f) S''(x_0) = S''(x_n) = 0


AUTHORS:

- Clinton Maurice Bowen (2014-06-08): initial version

EXAMPLES::


"""

#*****************************************************************************
#       Copyright (C) 2014 Clinton Maurice Bowen 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************




from sage.all import *
from sage.functions.piecewise import  PiecewisePolynomial
class NaturalCubicSpline(PiecewisePolynomial):
    '''
    This creates a natural cubic spline.
    
    See ISBN 0-534-39200-8
    '''
    
    def __init__(self,Data):
        '''
        Constructor
        input:
        Data = [(x0,y0),(x1,y1),...,(xn,yn)]
        description:
        creates cubic spline over domain (x0,xn)
        where qi(x) is defined over (x(i-1),xi) for i=1,2,...,n
        using sage maths PieceWise class.
        '''
        #Assert the data is sorted by x values, ascending
        self._n = len(Data) - 1# assume there are n+1 elements in Data
        self._data = sorted(Data,key=lambda tup:tup[0])
        self._X = [x[0] for x in self._data]
        self._Y = [y[1] for y in self._data]
        self._H = [self._X[i+1] - self._X[i] for i in range(self._n)]
        self._Alpha = [ (3/self._H[i]) * (self._Y[i+1] - self._Y[i]) - (3/self._H[i-1]) * (self._Y[i]-self._Y[i-1]) for i in range(1,self._n)         ]
        self._B, self._C, self._D = self.TridiagonalAlgorithm()
        x, functionList = self.GenerateFunctionList()
        PiecewisePolynomial.__init__(self,functionList, var=x)
    def GenerateFunctionList(self):
        '''
        this creates a set of intervals and splines as sage expressions
        '''
        x = var('x')
        functionList = [[(self._X[i],self._X[i+1]), self._Y[i] + self._B[i] * (x - self._X[i]) + self._C[i] * (x - self._X[i])*(x - self._X[i]) + self._D[i] * (x - self._X[i])*(x - self._X[i])*(x - self._X[i])] for i in range(self._n)]
        return x, functionList
    def TridiagonalAlgorithm(self):
        '''
        This derives the cubic polynomial coefficients for the natural cubic splines
        '''
        L   = [0.0] * (self._n+1)
        Mu  = [0.0] * (self._n)
        Z   = [0.0] * (self._n+1)#[z0, 
        L[0] = 1.0
        Mu[0] = 0.0
        Z[0] = 0.0
        B = [0.0] * (self._n)
        C = [0.0] * (self._n + 1)#[ c0, c1, ... c(n-2), c(n-1), cn]
        D = [0.0] * (self._n)
        for i in range(1,self._n):
            L[i]    = 2 * (self._X[i+1] - self._X[i-1]) - self._H[i-1] * Mu[i-1]
            Mu[i]   = self._H[i]/L[i]
            Z[i]    = (self._Alpha[i-1] - self._H[i-1] * Z[i-1])/L[i]
        L[self._n] = 1.0
        Z[self._n] = 0.0
        for i in range(self._n - 1, -1, -1):
            C[i] = Z[i] - Mu[i] * C[i+1]
            B[i] = (self._Y[i+1] - self._Y[i])/self._H[i] - self._H[i]*(C[i+1] + 2 * C[i])/3
            D[i] = (C[i+1] - C[i])/(3 * self._H[i])
        return B,C[0:len(C)-1],D 
            
        
