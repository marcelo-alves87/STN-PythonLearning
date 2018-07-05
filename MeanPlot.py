import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

def input_file_csv(filename, file_label, file_color, clazz):
    normalize_csv(filename)
    df = pd.read_csv(filename, low_memory=False)
    df.replace('?', -99999, inplace=True)
    df.fillna(-99999, inplace=True)
    df.drop(['id'], 1, inplace=True)
    xs = np.array(df.mean(axis=0))
    ys = np.full(len(xs), clazz, dtype=np.float64)
    plt.scatter(xs,ys, color=file_color, label=file_label)

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


input_file_csv('medidas/desgaste/H1N_FASE.csv', 'H1N', 'g', 1)
input_file_csv('medidas/desgaste/H1D10_FASE.csv', 'H1D10', 'b', 2)
input_file_csv('medidas/desgaste/H1D15_FASE.csv', 'H1D15', 'r', 2)
input_file_csv('medidas/desgaste/H1D25_FASE.csv', 'H1D25', 'k', 2)
input_file_csv('medidas/desgaste/H1D30-20_FASE.csv', 'H1D30-20', 'm', 2)
input_file_csv('medidas/desgaste/H1D50-20_FASE.csv', 'H1D50-20', 'c', 2)
input_file_csv('medidas/desgaste/H1D65_FASE.csv', 'H1D65', 'y', 2)
input_file_csv('medidas/desgaste/H1D75_FASE.csv', 'H1D75', 'yellow', 2)
input_file_csv('medidas/desgaste/H1D80_FASE.csv', 'H1D80', 'darkgray', 2)


plt.xlabel('Fase Hz')
plt.ylabel('Defined Classes')
plt.legend()
plt.show()

