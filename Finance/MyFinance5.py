import pandas as pd
import pickle
import pdb

def compile_data(until_date=None):
    
    with open("ibovespatickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        
        print(ticker)
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))

            df.set_index('Date', inplace=True)

            if until_date is not None:
                df = df.loc[:until_date]

            df.rename(columns={'Adj Close': ticker}, inplace=True)
            if 'Volume' in df.columns:
                df.drop(['Volume'], 1, inplace=True)
            if 'Open' in df.columns:
                df.drop(['Open', 'High', 'Low', 'Close'], 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')         
        except:
            pass
        
    print(main_df.head())
    main_df.to_csv('ibovespa_joined_closes.csv')


compile_data()
