import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import csv

style.use('seaborn-darkgrid')

fig = plt.figure()
ax1 = fig.add_subplot(111)

def animate(i):
    ax1.clear()
    input_file_csv('DTF')
    #input_file_csv('PHASe')
    #input_file_csv('SWR')
    #input_file_csv('SMITh')
    #input_file_csv('SMITh',2)


def input_file_csv(type1,column=1):
    xs, ys = normalize_csv(type1 + '.csv',column)
    plt.plot(xs,ys)
    #plt.plot(xs,ys, label=type1)
    
def normalize_csv(filename, column=1):
    xs = []
    ys = []
    end_index = 0
    
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            s = row[0]
            if(s.find('!') < 0 and s.find('BEGIN') < 0 and s.find('END') < 0):
                xs.append(row[0])
                ys.append(row[column])
    return np.array(xs, dtype=np.float64), np.array(ys, dtype=np.float64)
     

plt.xlabel('Frequencies (GHz)')
#plt.ylabel('MLOGarithmic (dB)')
#plt.ylabel('PHASe (Degrees)')
#plt.ylabel('SWR (dB)')
#plt.ylabel('Resistance (Ω)')
#plt.ylabel('Reactance (Ω)')

ani = animation.FuncAnimation(fig, animate, interval=1000)

#plt.legend()

plt.show()

