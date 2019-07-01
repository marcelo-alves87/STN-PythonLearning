import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

style.use('classic')

def input_file_csv(type1,angle=None):

    date = '08-03-2019' 
    normalize_csv(date,type1,angle)
   
    date = '11-03-2019'
    normalize_csv(date,type1,angle)
    
    date = '25-02-2019'
    normalize_csv(date,type1,angle)
    
    date = '26-02-2019'
    normalize_csv(date,type1,angle)
    
    date = '27-02-2019'
    normalize_csv(date,type1,angle)
    
def normalize_csv(date,type1,angle):
    if angle == None:
        csv_path = date + '/' + type1 + '/' 
    else:
        csv_path = date + '/' + type1 + '/' + angle + '/'  
    try:
        normalize_csv_(type1,date,csv_path + type1)
    except FileNotFoundError:
        normalize_csv_(type1,date,csv_path + 'DTF')

def normalize_csv_(type1,date,csv_path):
    x,y = normalize_csv__(csv_path + '.csv')
    plt.title(type1)
    plt.plot(x,y,label=date)
    
def normalize_csv__(filename):
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


input_file_csv('H1D25','0')
#input_file_csv('H1D30-20','0')
#input_file_csv('H1D50-20','0')
#input_file_csv('H1D65','0')
#input_file_csv('H1D75','0')
#input_file_csv('H1D80','0')
#input_file_csv('H1N')



#plt.xticks(np.arange(0, 5, step=0.1))
plt.xlabel('Meters')
plt.ylabel('VSWR')
plt.legend()
plt.grid()
plt.show()
