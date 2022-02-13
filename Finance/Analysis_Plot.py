import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import mplfinance as mpf
import pdb

style  = mpf.make_mpf_style(base_mpf_style='charles',mavcolors=['blue','orange','red'])

def RSI(df, window_length = 14):

    delta = df['Adj Close'].diff()
    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
    alpha = 1 / window_length
    roll_up = up.ewm(alpha=alpha).mean()
    roll_down = down.ewm(alpha=alpha).mean()
    rs = roll_up / roll_down
    rsi_rma = 100.0 - (100.0 / (1.0 + rs))
    return rsi_rma


##ticker = 'HAPV3'
##database = 'Old_Finance/Testes/2021-12-30/stock_dfs/'
###df = pd.read_csv('natura.csv', parse_dates=True, index_col=0)
##df = pd.read_csv(database + ticker + '.csv', parse_dates=True, index_col=0)
##df = df[100:]
##df['SMA'] = df['Adj Close'].rolling(window=40, min_periods=0).mean()
##df['EMA'] = df['Adj Close'].ewm(span=9, adjust=False).mean()
##
##
##df['RSI'] = RSI(df)
##
##style  = mpf.make_mpf_style(base_mpf_style='charles',mavcolors=['blue','orange','red'])
##fig = mpf.figure(style=style)
##
##count = 0
##
##hlines=[]
##pdb.set_trace()
##maximum = df['High'][-1]
##minimum = df['Low'][-1]
##diff = maximum - minimum
##hlines.append(maximum)
##hlines.append(minimum)
##
##
##fib = [23.6, 38.2, 61.8, 78.6]
##for f in fib:
##    hlines.append(diff*f/100 + minimum)
##    
##
##ax = fig.add_subplot(26,7,(1,38))
##av = fig.add_subplot(26,7,(43,45), sharex=ax)
##ar = fig.add_subplot(26,7,(50,52), sharex=ax)
##p = mpf.make_addplot(df['RSI'],ax=ar)
##mpf.plot(df,hlines=dict(hlines=hlines,colors=['g','r'],linestyle='--'),type='candle',ax=ax,mav=(5,8,13),axtitle='AAPL',addplot=p,volume=av, ylabel='', ylabel_lower='',xrotation=0)
##
##
##ax = fig.add_subplot(26,7,(5,42))
##av = fig.add_subplot(26,7,(47,49), sharex=ax)
##ar = fig.add_subplot(26,7,(54,56), sharex=ax)
##p = mpf.make_addplot(df['RSI'],ax=ar)        
##mpf.plot(df,type='candle',ax=ax,mav=(5,8,13),axtitle='AAPL', addplot=p,volume=av,ylabel='', ylabel_lower='',xrotation=0)
##


##size = 3
##capacity = size ** 2
##for i in range(size):
##    for j in range(1,size+1):
##        if count < 5:
##            group = size*(size*i) + j
##            ax = fig.add_subplot(capacity,size,group)
##            av = fig.add_subplot(capacity,size,group + size, sharex=ax)
##            ar = fig.add_subplot(capacity,size,group + 2*size, sharex=ax)
##            p = mpf.make_addplot(df['RSI'],ax=ar,ylabel='RSI')        
##            mpf.plot(df,type='candle',ax=ax,mav=(5,8,13),axtitle='AAPL', volume=av, addplot=p)
##        count += 1

def analysis(df):
    pdb.set_trace()

    

##plt.show()
