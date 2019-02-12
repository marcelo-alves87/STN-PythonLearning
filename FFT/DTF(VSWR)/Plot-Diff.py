import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

def input_file_csv(type1,parameter=1):
    type1_s = type1 + '-VF069'
    xs, ys = normalize_csv(type1_s + '.csv',parameter)
    plt.plot(xs,ys,label=type1_s)

    type1_s1 = type1 + '-VF079'
    xs1, ys1 = normalize_csv(type1_s1 + '.csv',parameter)
    plt.plot(xs1,ys1,label=type1_s1)
    
    #return xs,ys
    
def normalize_csv(filename,parameter=1):
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

#input_file_csv('A/H1N/DTF')
input_file_csv('A/H1D80/DTF')
#input_file_csv('A/H1D75/DTF')
#input_file_csv('A/H1D65/DTF')
#input_file_csv('A/H1D50-20/DTF')
#input_file_csv('A/H1D30-20/DTF')
#input_file_csv('A/H1D25/DTF')
#input_file_csv('A/H1D15/DTF')
#input_file_csv('A/H1D10/DTF')


plt.legend()
#plt.title('Diff DTF-H1D80A to Normal')
plt.grid()
#plt.gca().invert_yaxis()
plt.show()
