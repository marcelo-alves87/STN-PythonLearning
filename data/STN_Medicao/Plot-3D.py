import numpy as np
from mpl_toolkits.mplot3d import axes3d
from smithplot import SmithAxes
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle
from numpy.fft import fft, fftfreq, ifft

def plot_smith_chart(reals, imaginaries):
    ax = plt.subplot(111, projection='smith')
    plt.plot(50*reals,50*imaginaries, datatype=SmithAxes.Z_PARAMETER)
    plt.show()

def plot_ifft(frequencies, reals, imaginaries):
    x = 1/frequencies
    x = x[::-1]

    modulos = []
    for i,value in enumerate(reals):
        modulos.append(abs(complex(reals[i],imaginaries[i])))

    y_modulos = ifft(modulos)
    
    modulos = []
    for i,value in enumerate(y_modulos):
        modulos.append(abs(y_modulos[i]))

    plt.plot(x,modulos)
    plt.show()
    
def input_file_csv(type1):
    xs1, ys1 = normalize_csv(type1 + '.csv', 1)
    xs2, ys2 = normalize_csv(type1 + '.csv', 2)

    return xs1,ys1,ys2
    
def normalize_csv(filename, real_or_imaginary):
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
               if end_index == 4: 
                   break
               else:
                   xs = []
                   ys = []               
            elif(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                if len(row) > 2:
                    #1 Real, 2 Imaginary
                    ys.append(row[real_or_imaginary])
                else:
                    ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)
     
frequencies, reals, imaginaries = input_file_csv('L05c1-T176.2-EA/1GHz/NN-L05c1-T176.2-EA-1G')
plot_ifft(frequencies, reals, imaginaries)
plot_smith_chart(reals, imaginaries)



