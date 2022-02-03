import pandas as pd
import datetime as dt
import os
import pandas_datareader.data as web
import pdb
import yfinance as yfin


FREE_FLOAT = 'Free-Float_1-2022.csv'
yfin.pdr_override()

def date_to_str(date):
    return date.strftime('%Y-%m-%d')

def join_cells(x):    
    return ';'.join(x[x.notnull()].astype(str))

def check_interval(tickers,interval):
    ticker = tickers[0]
    path =  'stock_dfs/{}.csv'.format(ticker) 
    if os.path.exists(path):
        df = pd.read_csv(path)        
        date = dt.datetime.strptime(df.iloc[0]['Date'],'%Y-%m-%d')
        now = dt.datetime.now()
        days = now - date
        return days.days >= interval
    else:    
        return False
    
def update_data_from_yahoo(tickers, interval):
      
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    if not check_interval(tickers,interval):
        
        now = dt.date.today()
        start =  now - dt.timedelta(days=interval)    
        tomorrow = now + dt.timedelta(days=1)    
        
        for ticker in tickers:
            print(ticker)
            # just in case your connection breaks, we'd like to save our progress!
            if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
                try:
                    df = web.get_data_yahoo(ticker + '.SA', start=start.strftime('%Y-%m-%d'), end=tomorrow.strftime('%Y-%m-%d'))
                    df.to_csv('stock_dfs/{}.csv'.format(ticker))           
                except:
                    print(ticker,'não foi encontrado')
            else:
                print('Already have {}'.format(ticker))


def get_tickers_from_free_float():
    df = pd.read_csv(FREE_FLOAT, sep=';')
    return df['Codigo']


def create_df_from_free_float(interval):

    tickers = get_tickers_from_free_float()

    
    
    update_data_from_yahoo(tickers,interval)

    
    df_tickers = pd.DataFrame()

    

    for ticker in tickers:
       
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        
        df['Date'] = df['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))
        df.set_index('Date',inplace=True)
        now = dt.datetime.now()
        start =  now - dt.timedelta(days=interval)
        df = df[(df.index >= start)]
        
        if len(df) > 0:
            df['Var.'] = (1 - (df['Open']/df['High']))*100
            df['Ticket'] = ticker
            df.reset_index(inplace=True)
            df_tickers = pd.concat([df_tickers, df])

    #df_tickers['Date'] = df_tickers['Date'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))


    df_tickers.set_index('Date',inplace=True)
    return df_tickers


def ranking_tickets_by_var(interval=30):
    df_tickers = create_df_from_free_float(interval)
    #grouping by index
    df_tickers['Score'] = df_tickers.groupby(level=0)['Var.'].rank(ascending=True)
   
    group = df_tickers.groupby('Ticket').agg({'Score': 'sum', 'Volume' : 'first'})
    
    group = group.sort_values(['Volume', 'Score'],ascending=False)
    group['Volume'] = group['Volume'] / 10 ** 6 
    print('Rank of elements from {} to {}:'.format(date_to_str(df_tickers.iloc[0].name), date_to_str(df_tickers.iloc[-1].name)))
    group.reset_index(inplace=True)
    for i,row in group.iterrows():
        
        print('{} {} : Score({}) Volume({}) M'.format(i+1,row['Ticket'],int(row['Score']),round(row['Volume'],3)))
        
#if interval is lower than 30, update will not be executed
ranking_tickets_by_var(interval=5)

        
