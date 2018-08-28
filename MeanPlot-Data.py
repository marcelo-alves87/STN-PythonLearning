import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

filename = 'data/STN_DATA_DESGASTE_MEDIA.csv'

df = pd.read_csv(filename, low_memory=False)


def normalize_csv(filename):
    needToNorm = True
    read = open(filename).read()
    if 'id,' in read:
        needToNorm = False    
           
    if needToNorm:
        newText=read.replace(',','.') 
        newText=newText.replace(';',',')

        with open(filename, "w") as f:
            f.write(newText)

def input_class(df, clazz, color, lastsize=0):
    df = df.loc[df['class'] == clazz]
    df.drop(['class'], 1, inplace=True)
    ys = np.array(df.mean(axis=1))
    xs = np.arange(len(ys))
    print(clazz,': ', len(ys))
    plt.scatter(xs + lastsize,ys, color=color)
    return len(ys)

normalize_csv(filename)
df = pd.read_csv(filename, low_memory=False)
df.replace('?', -99999, inplace=True)
df.fillna(-99999, inplace=True)
df.drop(['id'], 1, inplace=True)
size = input_class(df, 1, 'g')
input_class(df, 2, 'b', size)

plt.xlabel('Measure')
plt.ylabel('|S11| dB Mean')
plt.show()
