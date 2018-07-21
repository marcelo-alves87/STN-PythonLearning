import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

filename = 'data/STN_DATA_DESGASTE_MEDIA.csv'

df = pd.read_csv(filename, low_memory=False)

def input_class(df, clazz, color):
    df = df.loc[df['class'] == clazz]
    df.drop(['class'], 1, inplace=True)
    ys = np.array(df.mean(axis=1))
    xs = np.arange(len(ys))
    print(clazz,': ', len(ys))
    plt.scatter(xs,ys, color=color)

df = pd.read_csv(filename, low_memory=False)
df.replace('?', -99999, inplace=True)
df.fillna(-99999, inplace=True)
df.drop(['id'], 1, inplace=True)
input_class(df, 1, 'g')
input_class(df, 2, 'b')

plt.xlabel('Measure')
plt.ylabel('Value')
plt.show()
