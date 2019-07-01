import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

style.use('dark_background')

dates = ['08-03-2019','11-03-2019','25-02-2019','26-02-2019','27-02-2019']

def input_file_csv(type1,angle=None):
   #input_file_csv_(type1,'0','DVHR')
   #input_file_csv_(type1,'90','DVPN')
   #input_file_csv_(type1,'180','DVCR')
   input_file_csv_(type1,angle)
   
def input_file_csv_(type1,angle=None,label=None):
    y = []
    x = []
    for date in dates:
        x,y1 = normalize_csv(date,type1,angle)
        y.append(y1)
    y = np.mean(y,axis=0)
    for i in range(48,93):
       #print(y[i])
       plt.plot(x[48:100],y[48:100],label=type1,c='y',marker="D",markevery=[26,32]) 

def normalize_csv(date,type1,angle):
   if angle == None:
      csv_path = date + '/' + type1 + '/'
   else:      
      csv_path = date + '/' + type1 + '/' + angle + '/'  
   try:
        return normalize_csv_(csv_path + type1)
   except:
      try:
            return normalize_csv_(csv_path + 'DTF')
      except:
         try:
                return normalize_csv_(date + '/' + type1 + '/' + 'DTF')
         except:
                return normalize_csv_(date + '/' + type1 + '/' + type1)
            
def normalize_csv_(csv_path):
    return normalize_csv__(csv_path + '.csv')
    
    
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


#input_file_csv('H1D25','0')
#input_file_csv('H1D30-20')
input_file_csv('H1D50-20','0')
#input_file_csv('H1D65')
#input_file_csv('H1D75')
#input_file_csv('H1D80','0')
#input_file_csv('H1N')



plt.xticks(np.arange(1.2,2.5,step=0.1))
plt.xlabel('Meters')
plt.ylabel('VSWR')
plt.legend(prop= {'size' : 20})
plt.grid()
plt.show()
