import threading
import Analysis_Trend as at
import Analysis_Voice as av
import Utils as utils
import datetime as dt
import pdb
PICKLE_FILE_TEST = 'btc_tickers_test.plk'
PICKLE_FILE = 'btc_tickers.plk'

df = utils.try_to_get_df(PICKLE_FILE)
utils.save_df(PICKLE_FILE_TEST,df)
date = dt.datetime.strptime('2022-02-10 16:45:00','%Y-%m-%d %H:%M:%S')
x = threading.Thread(target=av.run, args=(PICKLE_FILE_TEST,))
for i in range(90):
    new_date =  date + dt.timedelta(minutes=i)    
    df = df[df['Hora'] < new_date.strftime("%Y-%m-%d %H:%M:%S")]
    utils.save_df(PICKLE_FILE_TEST,df)
    if not x.is_alive():
        x.start()


