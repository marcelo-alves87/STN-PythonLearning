import time
from gtts import gTTS
from pygame import mixer


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

    

