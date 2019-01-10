import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv

style.use('seaborn-darkgrid')

markers = ['x', 'o', 'P', 's']

def input_file_csv(type1, clazz=1):
    xs = []
    #1 S11, 2 Phase, 3 SWR, 4 Real/Imaginary
    #1 Real, 2 Imaginary
  
    mean = 0
      
    ys11 = []   
    normalize_csv(type1 + '.csv', 1, 1, xs, ys11)
    ys11 = np.array(ys11, dtype=np.float64)
    mean += ys11.mean(axis=0)

    yPhase = []   
    normalize_csv(type1 + '.csv', 2, 1, xs, yPhase)
    yPhase = np.array(yPhase, dtype=np.float64)
    mean += yPhase.mean(axis=0)

    ySWR = []   
    normalize_csv(type1 + '.csv', 3, 1, xs, ySWR)
    ySWR = np.array(ySWR, dtype=np.float64)
    mean += ySWR.mean(axis=0)

    yZinReal = []   
    normalize_csv(type1 + '.csv', 4, 1, xs, yZinReal)
    yZinReal = np.array(yZinReal, dtype=np.float64)
    mean += yZinReal.mean(axis=0)
    
    yZinImaginary = []   
    normalize_csv(type1 + '.csv', 4, 2, xs, yZinImaginary)
    yZinImaginary = np.array(yZinImaginary, dtype=np.float64)
    mean += yZinImaginary.mean(axis=0)

    global x
    x += 1
    
    plt.scatter(mean,clazz, label=type1,marker=markers[(x-1)%len(markers)])

def normalize_csv(filename, parameter, impedance, xs, ys):
    begin_index = 0
    is_to_append = False
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if s.find('BEGIN') >= 0:
               begin_index += 1 
               if begin_index == parameter:
                   is_to_append = True
            elif s.find('END') >= 0:
               if begin_index == parameter:
                   break    
            elif(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                if is_to_append:
                    if not len(xs) == 1001:
                        xs.append(row[0])
                    if len(row) > 2:
                        ys.append(row[impedance])
                    else:
                        ys.append(row[1])
          

def input_files_csv():
    input_file_csv('L05c1-T176.2-EA/1GHz/NN-L05c1-T176.2-EA-1G')
    input_file_csv('L05c1-T176.2-EB/1GHz/NN-L05c1-T176.2-EB-1G')
    input_file_csv('L05c1-T176.2-ED/1GHz/NN-L05c1-T176.2-ED-1G')
    input_file_csv('L05c1-T188.1-EA/1GHz/NN-L05c1-T188.1-EA-1G')
    input_file_csv('L05c1-T188.1-EB/1GHz/NN-L05c1-T188.1-EB-1G')
    input_file_csv('L05c1-T188.1-EC/1GHz/NN-L05c1-T188.1-EC-1G',2)
    input_file_csv('L05c1-T188.1-ED/1GHz/NN-L05c1-T188.1-ED-1G')
    input_file_csv('L05c1-T189.1-EA/1GHz/NN-L05c1-T189.1-EA-1G',2)
    input_file_csv('L05c1-T189.1-EB/1GHz/NN-L05c1-T189.1-EB-1G')
    input_file_csv('L05c1-T189.1-EC/1GHz/NN-L05c1-T189.1-EC-1G')
    input_file_csv('L05c1-T189.1-ED/1GHz/NN-L05c1-T189.1-ED-1G',2)
    input_file_csv('L05c1-T197.2-EB/1GHz/NN-L05c1-T197.2-EB-1G',2)
    input_file_csv('L05c1-T197.2-EC/1GHz/NN-L05c1-T197.2-EC-1G')
    input_file_csv('L05c1-T205.1-EA/1GHz/NN-L05c1-T205.1-EA-1G')
    input_file_csv('L05c1-T205.1-EB/1GHz/NN-L05c1-T205.1-EB-1G',2)
    input_file_csv('L05c1-T205.1-EC/1GHz/NN-L05c1-T205.1-EC-1G',2)
    input_file_csv('L05c1-T205.1-ED/1GHz/NN-L05c1-T205.1-ED-1G',2)
        
x = 0
input_files_csv()
plt.xlabel('Mean (MLOGarithmic, PHASe, SWR, Resistance, Reactance)')
plt.ylabel('Class')
plt.legend(loc=1, prop={'size': 6})
plt.show()