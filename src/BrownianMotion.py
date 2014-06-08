'''
Created on Apr 5, 2014

@author: Jas
'''
from sage.all import *
def GetBownianMotionVector(En):
    '''
    returns a sage vector of RealDoubleField() with brownian motion values of size N
    '''
    return BrownianMotion.GetVector(En)

def GetBrownianMotionVectorAlongF(En,f): 
    brownianMotion = BrownianMotion.GetVector(En)
    F = [f(v) for v in brownianMotion]
    return vector(F)

def GetExponentialBrownianVector(En,x0,k):
    f = lambda t: x0 * exp(k * t)
    return GetBrownianMotionVectorAlongF(En,f)
    
class BrownianMotion(SageObject):
    '''
    classdocs
    
    2. Brownian Motion. A scalar standard Brownian motion, or standard Wiener process, 
       over [0, T ] is a random variable W (t) that depends continuously on t in [0, T ] 
       and satisfies the following three conditions.
            1. W (0) = 0 (with probability 1). 
            2. For 0 <= s < t <= T the random variable given by the increment W(t)-W(s) is
               normally distributed with mean zero and variance t - s; equivalently, 
               W (t) - W (s) ~ sqrt(t - s) N (0, 1), where N (0, 1) denotes a normally distributed 
               random variable with zero mean and unit variance.
            3. For0<=s<t<u<v<=T theincrements W(t)-W(s) and W(v)-W(u) are independent.
    '''
    @staticmethod
    def GetVector(en):
        '''
        returns a vector of brownian motion from N(0,1)
        '''
        zVector = vector(RealDoubleField(),en)#represents all the dW ~ sqrt(delta * t) N(0,1)
        yVector = vector(RealDoubleField(),en)
        Omega = RealDistribution('gaussian',1)
        for i in range(1,len(zVector)):
            zVector[i] = (1.0/float(en)) * Omega.get_random_element()#represents all the dW ~ sqrt(delta * t) N(0,1)
            yVector[i] = zVector[i] + yVector[i-1] # W_t = dW_t + W_{t-1}
        return yVector
    def __init__(self):
        pass