import datetime as dt
import time
from gtts import gTTS
from pygame import mixer
import pandas as pd
import pdb
import pickle
import os

def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)

def convert_to_str(x,format='%Y-%m-%d %H:%M:%S'):
    return x.strftime(format)

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

def try_to_get_df(file_path):
    df = None
    while df is None:
        try:
            df = pd.read_pickle(file_path)
        except:
            pass
    return df

def save_df(file_path,df):
   df = df.to_pickle(file_path)
    
def get_pickle_file(file_path):    
    if os.path.exists(file_path): 
        with open(file_path,"rb") as f:
            return pickle.load(f)
    else:
        return None

def save_pickle_file(file_path,data):
     with open(file_path,"wb") as f:
        pickle.dump(data,f)

def RSI(df, window_length = 14):

    delta = df.diff()
    up, down = delta.clip(lower=0), delta.clip(upper=0).abs()
    alpha = 1 / window_length
    roll_up = up.ewm(alpha=alpha).mean()
    roll_down = down.ewm(alpha=alpha).mean()
    rs = roll_up / roll_down
    rsi_rma = 100.0 - (100.0 / (1.0 + rs))
    rsi_rma.fillna(0)
    return rsi_rma
