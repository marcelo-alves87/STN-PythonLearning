import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

filename = 'data/18-05-18/Deteccao do Nivel/STN_Rev.Nivel_1.csv'

def input_class(df, clazz, color):
    df = df.loc[df['class'] == clazz]
    ys = np.array(df['class'])
    df.drop(['class'], 1, inplace=True)
    xs = np.array(df.mean(axis=1))
    plt.scatter(xs,ys, color=color)

df = pd.read_csv(filename, low_memory=False)
df.replace('?', -99999, inplace=True)
df.fillna(-99999, inplace=True)
#df.drop(['id'], 1, inplace=True)

input_class(df, 0, 'g')
input_class(df, 1, 'b')
input_class(df, 2, 'r')
input_class(df, 3, 'y')
##input_class(df, 80, 'w')
##input_class(df, 100, 'c')


plt.xlabel('Values')
plt.ylabel('Defined Classes')
plt.show()
