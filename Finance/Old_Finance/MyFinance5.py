import pandas as pd
import pickle
import pdb
import os
def compile_data(start_date = None, end_date = None):
    
##    with open("ibovespatickers.pickle", "rb") as f:
##        tickers = pickle.load(f)
    tickers = []
    for file_path in os.listdir('stock_dfs'):
        tickers.append(file_path.replace('.csv',''))

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        
        print(ticker)
        try:
            
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))

            df.set_index('Datetime', inplace=True)

            if start_date is not None:
                df = df.loc[start_date:]

            if end_date is not None:
                df = df.loc[:end_date]    

            df.rename(columns={'Close': ticker}, inplace=True)

            df = df[[ticker]]

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')         
        except:
            pass
        
    print(main_df.head())
    main_df.to_csv('ibovespa_joined_closes.csv')


compile_data()
