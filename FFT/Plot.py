import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

style.use('seaborn-darkgrid')

def input_file_csv(type1):
    xs, ys = normalize_csv(type1 + '.csv')
    return xs, ys
    
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
     
xs,ys = input_file_csv('/H1-A/HC1N')
plt.plot(xs,ys)
plt.show()
