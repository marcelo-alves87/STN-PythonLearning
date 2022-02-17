import threading
import Analysis_Trend as at
import Analysis_Voice as av
import Utils as utils
import datetime as dt
import pdb
import time

PICKLE_FILE = 'btc_tickers.plk'
PICKLE_FILE_TEST = 'btc_tickers_test.plk'



def increment_date(date,df):
    input('Start ...')
    i = 0
    while True:
        
        date1 =  date + dt.timedelta(minutes=i)    
        df2 = df[df['Hora'] < date1.strftime("%Y-%m-%d %H:%M:%S")]
        utils.save_df(PICKLE_FILE_TEST,df2)
        i += 1
        time.sleep(3)


def test():
    date = dt.datetime.strptime('2022-02-16 10:00:00','%Y-%m-%d %H:%M:%S')
    df = utils.try_to_get_df(PICKLE_FILE)
    utils.save_df(PICKLE_FILE_TEST,df)
    x = threading.Thread(target=increment_date, args=(date,df,))
    x.start()
    y = threading.Thread(target=av.run, args=(PICKLE_FILE_TEST,))
    y.start()
    at.run(PICKLE_FILE_TEST)


def run():
    df = utils.try_to_get_df(PICKLE_FILE)
    at.run(df)
    
test()
