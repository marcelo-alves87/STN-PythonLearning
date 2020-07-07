import skrf as rf
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

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
                if len(row) > 1:
                    #1 Real, 2 Imaginary
                    ys.append(row[1])
                else:
                    ys.append(row[1])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)

def vswr(data):
    return (1 + data) / (1 - data)

plt.rc('font', family='arial')
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')
#plt.rc('text', usetex=True)
fig = plt.figure(figsize=(4, 4))
ax = fig.add_subplot(1, 1, 1)

#probe = rf.Network('H2D80-20/H2D80-20.s1p')
#x,y = probe.plot_s_db_time(window=('kaiser', 6))
#plt.plot(0.92*3*10**8*x/2,smooth(y,3),,  linewidth=2)
x,y= normalize_csv('11-03-2019/H1D80/0/H1D80.csv')

#x = np.linspace(0.0, 5, 201)
#ax.plot(x/2,smooth(y,3), color='orange', ls='solid')
ax.plot(x, y, color='blue')
ax.set_xlabel('Metro (m)')
ax.set_ylabel('VSWR')
ax.set_xlim(0, 2.05)
ax.set_ylim(1,1.05)
plt.grid()
plt.show()

