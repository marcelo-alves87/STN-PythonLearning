import numpy as np
from sklearn import preprocessing, cross_validation, neighbors
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

df = pd.read_csv('breast-cancer-wisconsin.data.txt')
df.replace('?', -99999, inplace=True)
df.drop(['id'], 1, inplace=True)

y = np.array(df['class'])
X = df.drop(['class'], 1)
X = np.array(X.mean(axis=1))

plt.scatter(X,y)

plt.show()
