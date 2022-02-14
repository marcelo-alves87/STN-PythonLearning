import datetime as dt
import time
from gtts import gTTS
from pygame import mixer
import pandas as pd
import pdb

PICKLE_FILE = 'btc_tickers.plk'

def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)    

def convert_to_datetime(x):
    if isinstance(x,str):    
        if x != x: #is nan
            return ''
        elif x == '':
            return ''
        else:            
            return dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')
    else:
        return x
                
            
def play(text, path, language):
    
    try:
        myobj = gTTS(text=text, lang=language)
        myobj.save(path)
        mixer.init()
        mixer.music.load(path)
        mixer.music.play()
        time.sleep(3)
    except:
        pass

    

def to_volume(x):
    if isinstance(x,str):        
        x = x.replace(',','.')
        value = float(x[:-1])
        s = x[-1]
        if s == 'k':
            return value * (10 ** 3)
        elif s == 'M':
            return value * (10 ** 6)
        elif s == 'B':
            return value * (10 ** 9)
    else:       
        return float(x)

def try_to_get_df():
    df = None
    while df is None:
        try:
            df = pd.read_pickle(PICKLE_FILE)
        except:
            pass
    return df    
    
