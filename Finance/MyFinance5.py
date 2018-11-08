import pandas as pd
import pickle

def compile_data():
    with open("ibovespatickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        print(ticker)
        try:
            df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))

            df.set_index('Date', inplace=True)

            df.rename(columns={'Adj Close': ticker}, inplace=True)
            df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')         
        except:
            pass
        
    print(main_df.head())
    main_df.to_csv('ibovespa_joined_closes.csv')


compile_data()
