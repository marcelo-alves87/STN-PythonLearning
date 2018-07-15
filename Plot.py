import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import style
import sys

style.use('fivethirtyeight')

def input_file_csv(filename, file_label, file_color):
    normalize_csv(filename)
    df = pd.read_csv(filename, low_memory=False)
    df.replace('?', -99999, inplace=True)
    df.fillna(-99999, inplace=True)
    xs = np.array(df['id'])
    df.drop(['id'], 1, inplace=True)
    ys = np.array(df.std(axis=1))
    plt.plot(xs,ys, color=file_color, label=file_label)
                    
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
            

input_file_csv('data/medidas/H1N.csv', 'H1N', 'g')
input_file_csv('data/medidas/H1D10.csv', 'H1D10', 'b')
input_file_csv('data/medidas/H1D15.csv', 'H1D15', 'r')
input_file_csv('data/medidas/H1D25.csv', 'H1D25', 'k')
input_file_csv('data/medidas/H1D30-20.csv', 'H1D30-20', 'm')
input_file_csv('data/medidas/H1D50-20.csv', 'H1D50-20', 'c')
input_file_csv('data/medidas/H1D65.csv', 'H1D65', 'y')
input_file_csv('data/medidas/H1D75.csv', 'H1D75', 'yellow')
input_file_csv('data/medidas/H1D80.csv', 'H1D80', 'darkgray')


##input_file_csv('data/medidas/H1N_FASE.csv', 'H1N_FASE', 'g')
##input_file_csv('data/medidas/H1D10_FASE.csv', 'H1D10_FASE', 'b')
##input_file_csv('data/medidas/H1D15_FASE.csv', 'H1D15_FASE', 'r')
##input_file_csv('data/medidas/H1D25_FASE.csv', 'H1D25_FASE', 'k')
##input_file_csv('data/medidas/H1D30-20_FASE.csv', 'H1D30-20_FASE', 'm')
##input_file_csv('data/medidas/H1D50-20_FASE.csv', 'H1D50-20_FASE', 'c')
##input_file_csv('data/medidas/H1D65_FASE.csv', 'H1D65_FASE', 'y')
##input_file_csv('data/medidas/H1D75_FASE.csv', 'H1D75_FASE', 'yellow')
##input_file_csv('data/medidas/H1D80_FASE.csv', 'H1D80_FASE', 'darkgray')

plt.xlabel('Frequency (MHz)')
plt.ylabel('Standard Deviation (σ)')
plt.legend()
plt.show()

