import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv

style.use('fivethirtyeight')

def input_file_csv(type1):
    xs, ys = normalize_csv(type1 + '.csv')
    plt.plot(xs,ys)

def normalize_csv(filename):
    xs = []
    ys = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)
     
input_file_csv('MLOGarithmic')
#input_file_csv('PHASe')
#input_file_csv('SWR')


plt.xlabel('Frequencies')
plt.ylabel('Values')    
plt.show()

