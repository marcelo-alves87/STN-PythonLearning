import datetime as dt
import time
from gtts import gTTS
from pygame import mixer


def convert_to_float(x):
    if x is None or x == '':
        return 0
    else:
        return float(x)    

def convert_to_datetime(x):
        
    if x != x: #is nan
        return ''
    elif x == '':
        return ''
    else:            
        return dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S')           
            
            
def play(text, path, language):
    myobj = gTTS(text=text, lang=language)
    try:
        myobj.save(path)
    except:
        pass

    mixer.init()
    mixer.music.load(path)
    mixer.music.play()
    time.sleep(3)

def to_volume(x):    
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


