import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

def input_file_csv(type1,parameter=1):
    xs, ys = normalize_csv(type1 + '.csv',parameter)
    #plt.plot(xs,ys,label=type1)
    return xs,ys
    
def normalize_csv(filename,parameter):
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
               if end_index == parameter: 
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

xs,ys = input_file_csv('H1N/A/H1NA',2)
xs1, ys1 = input_file_csv('H1N/A/H1D80A',2)
plt.plot(xs, ys-ys1)
#plt.legend()
plt.title('Diff DTF-H1D80A to Normal')
plt.grid()
plt.gca().invert_yaxis()
plt.show()
