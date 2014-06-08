'''
Created on Apr 4, 2014

@author: Jas

%EM Euler-Maruyama method on linear SDE
%SDE is dX = lambda*X dt+mu*X dW, X(0)=Xzero
%where lambda = 2,mu = 1 and Xzero = 1
%discretized brownian path over [0,1] has dt = 2^(-8)
%Euler maruyuma uses timestep R*dt.
randn('state',100)
lambda = 2;mu = 1;Xzero = 1; % given parameters in problem
T=1; N = 2^8;dt =1/N;
dW = sqrt(dt)*randn(1,N);% Brownian increments 
W = cumsum(dW);% Here we are discretized the brownian path with cumulative sum

Xtrue = Xzero*exp((lambda-0.5*mu^2)*([dt:dt:T])+mu*W);% exact solution to the SDE
plot([0:dt:T],[Xzero,Xtrue],'b-'),hold on 


R=4;Dt =R*dt;L =N/R;% Step size Dt = R*dt where dt = 1/N Which is 1/2^8 
%dt = 2^-8 so Dt = 4*2^-8, L = 2^8/4=
Xem = zeros(1,L);% the 1 by L array Xem stores the EM solution 
% Preallocate array for efficiency , we use when variable is not defined
% earlier so here Xem has not so far been assigned.
Xtemp = Xzero;
for j = 1:L 
    Winc = sum (dW(R*(j-1)+1:R*j));
    Xtemp = Xtemp+Dt*lambda*Xtemp+mu*Xtemp*Winc;%EM method to the linear SDE
    %dX(t) = LambdaX(t)dt+muX(t)dt, X(0)= X0
    Xem(j)=Xtemp;
end
xtime = [0:Dt:T];
plot(xtime,[Xzero,Xem],'r--*'),hold on
legend('Exact Solution','Euler-Maruyama Method Approximation'),hold on
title('Euler-Maruyama Method on Linear SDE')
xlabel('t','FontSize',12)
ylabel('X','FontSize',16,'Rotation',0,'HorizontalAlignment','right')
hold off
emerr= abs(Xem(end)-Xtrue(end))% computed emerr found and taking R delta t 
%with smaller R values of 2 and 1 produced endpoint errors of 0.1595 and
%0.0821
'''
from Stock import Stock
from sage.all import *
from numpy.random import randn
from BrownianMotion import GetExponentialBrownianVector
def frange(x, y, jump):
    while x < y:
        yield x
        x += jump
class EulerMaruyama(Stock):
    '''
    classdocs
    '''

    def GenerateStockPrices(self,en):
        '''
        randn('state',100)
        lambda = 2;mu = 1;Xzero = 1; % given parameters in problem
        T=1; N = 2^8;dt =1/N;
        dW = sqrt(dt)*randn(1,N);% Brownian increments 
        W = cumsum(dW);% Here we are discretized the brownian path with cumulative sum
        
        Xtrue = Xzero*exp((lambda-0.5*mu^2)*([dt:dt:T])+mu*W);% exact solution to the SDE
        plot([0:dt:T],[Xzero,Xtrue],'b-'),hold on 
        
        
        R=4;Dt =R*dt;L =N/R;% Step size Dt = R*dt where dt = 1/N Which is 1/2^8 
        %dt = 2^-8 so Dt = 4*2^-8, L = 2^8/4=
        Xem = zeros(1,L);% the 1 by L array Xem stores the EM solution 
        % Preallocate array for efficiency , we use when variable is not defined
        % earlier so here Xem has not so far been assigned.
        Xtemp = Xzero;
        for j = 1:L 
            Winc = sum (dW(R*(j-1)+1:R*j));
            Xtemp = Xtemp+Dt*lambda*Xtemp+mu*Xtemp*Winc;%EM method to the linear SDE
            %dX(t) = LambdaX(t)dt+muX(t)dt, X(0)= X0
            Xem(j)=Xtemp;
        end
        '''
        Lambda = 2.0
        mu = 2#mu * X = sigma(x)  We need to throw this variable high to make the SDE to behave as a bubble.
        X0 = 100.0
        T = 1.0
        En = 2**en
        dt = 1.0/En
        dW = sqrt(dt) * vector(randn(1,En)[0].tolist()) #+ mu * vector(ones_matrix(1,En).list())
        R=4.0
        Dt =R*dt
        L =En/R
        Xem = zero_vector(RealDoubleField(),L)
        Xtemp = X0
        for j in range(int(L)):
            Winc = sum(dW[int(R*j):int(R*(j+1)) - 1])
            Xtemp += Dt*Lambda*Xtemp+mu*Xtemp*Winc
            Xem[j] = Xtemp
        return Xem;
    
    def __init__(self,en):
        '''
        Constructor
        Input:
        en - Number of samples to create
        Output  an inherited Stock class with this.StockPrices to have 2**(n-2) entries
        '''
        #self.StockPrices = self.GenerateStockPrices(en)
        k = 2
        x0=100
        self.StockPrices = GetExponentialBrownianVector(2**(en-2),x0,k)
        self.Ticker = None
        self.CompanyName = None
        self.maxPrice = max(self.StockPrices)
        self.minPrice = min(self.StockPrices)