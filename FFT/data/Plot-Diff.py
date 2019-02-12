import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

def input_file_csv(type1):
    xs, ys = normalize_csv(type1 + '.csv')
    #return xs,ys
    plt.plot(xs,ys,label=type1)

def normalize_csv(filename):
    xs = []
    ys = []
    end_index = 0
    
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if s.find('END') >= 0:
               end_index += 1 
               #1 S11, 2 Phase, 3 SWR, 4 Real/Imaginary 
               if end_index == 1: 
                   break
               else:
                   xs = []
                   ys = []               
            elif(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                if len(row) > 2:
                    #1 Real, 2 Imaginary
                    ys.append(row[1])
                else:
                    ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)

input_file_csv('H1-A/HC1N')

#input_file_csv('H1-A/HC1D10')
input_file_csv('H1-A/HC1D20')
#input_file_csv('H1-A/HC1D70')
#input_file_csv('H1-A/HC1D80')

input_file_csv('H1-A/HC1D15-5')
#input_file_csv('H1-A/HC1D80-5')

input_file_csv('H1-A/HC1D20M')
#input_file_csv('H1-A/HC1D40M')
#input_file_csv('H1-A/HC1D50M')
#input_file_csv('H1-A/HC1D70M')
#input_file_csv('H1-A/HC1D80M')

plt.legend()
plt.grid()
plt.gca().invert_yaxis()
plt.show()
