import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import csv
import pickle

style.use('seaborn-darkgrid')

def input_file_csv(type1):
    xs, ys = normalize_csv(type1 + '.csv')

    with open(type1 + '.pickle', 'wb') as f:
        pickle.dump(ys,f)
        
    plt.plot(xs,ys, label=type1)

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
     
#input_file_csv('L05c1-T176.2-EA/1GHz/NN-L05c1-T176.2-EA-1G')
##input_file_csv('L05c1-T176.2-EA/1GHz/NS-L05c1-T176.2-EA-1G')
##input_file_csv('L05c1-T176.2-EA/1GHz/SN-L05c1-T176.2-EA-1G')
##input_file_csv('L05c1-T176.2-EA/1GHz/SS-L05c1-T176.2-EA-1G')
##input_file_csv('L05c1-T176.2-EA/6GHz/NN-L05c1-T176.2-EA-6G')
##input_file_csv('L05c1-T176.2-EA/6GHz/NS-L05c1-T176.2-EA-6G')
##input_file_csv('L05c1-T176.2-EA/6GHz/SN-L05c1-T176.2-EA-6G')
##input_file_csv('L05c1-T176.2-EA/6GHz/SS-L05c1-T176.2-EA-6G')
##
#input_file_csv('L05c1-T176.2-EB/1GHz/NN-L05c1-T176.2-EB-1G')
##input_file_csv('L05c1-T176.2-EB/1GHz/NS-L05c1-T176.2-EB-1G')
##input_file_csv('L05c1-T176.2-EB/1GHz/SN-L05c1-T176.2-EB-1G')
##input_file_csv('L05c1-T176.2-EB/1GHz/SS-L05c1-T176.2-EB-1G')
##input_file_csv('L05c1-T176.2-EB/6GHz/NN-L05c1-T176.2-EB-6G')
##input_file_csv('L05c1-T176.2-EB/6GHz/NS-L05c1-T176.2-EB-6G')
##input_file_csv('L05c1-T176.2-EB/6GHz/SN-L05c1-T176.2-EB-6G')
##input_file_csv('L05c1-T176.2-EB/6GHz/SS-L05c1-T176.2-EB-6G')

#input_file_csv('L05c1-T176.2-ED/1GHz/NN-L05c1-T176.2-ED-1G')
##input_file_csv('L05c1-T176.2-ED/1GHz/NS-L05c1-T176.2-ED-1G')
##input_file_csv('L05c1-T176.2-ED/1GHz/SN-L05c1-T176.2-ED-1G')
##input_file_csv('L05c1-T176.2-ED/1GHz/SS-L05c1-T176.2-ED-1G')
##input_file_csv('L05c1-T176.2-ED/6GHz/NN-L05c1-T176.2-ED-6G')
##input_file_csv('L05c1-T176.2-ED/6GHz/NS-L05c1-T176.2-ED-6G')
##input_file_csv('L05c1-T176.2-ED/6GHz/SN-L05c1-T176.2-ED-6G')
##input_file_csv('L05c1-T176.2-ED/6GHz/SS-L05c1-T176.2-ED-6G')
##

#input_file_csv('L05c1-T188.1-EA/1GHz/NN-L05c1-T188.1-EA-1G')
##input_file_csv('L05c1-T188.1-EA/1GHz/NS-L05c1-T188.1-EA-1G')
##input_file_csv('L05c1-T188.1-EA/1GHz/SN-L05c1-T188.1-EA-1G')
##input_file_csv('L05c1-T188.1-EA/1GHz/SS-L05c1-T188.1-EA-1G')
##input_file_csv('L05c1-T188.1-EA/6GHz/NN-L05c1-T188.1-EA-6G')
##input_file_csv('L05c1-T188.1-EA/6GHz/NS-L05c1-T188.1-EA-6G')
##input_file_csv('L05c1-T188.1-EA/6GHz/SN-L05c1-T188.1-EA-6G')
##input_file_csv('L05c1-T188.1-EA/6GHz/SS-L05c1-T188.1-EA-6G')

#input_file_csv('L05c1-T188.1-EB/1GHz/NN-L05c1-T188.1-EB-1G')
##input_file_csv('L05c1-T188.1-EB/1GHz/NS-L05c1-T188.1-EB-1G')
##input_file_csv('L05c1-T188.1-EB/1GHz/SN-L05c1-T188.1-EB-1G')
##input_file_csv('L05c1-T188.1-EB/1GHz/SS-L05c1-T188.1-EB-1G')
##input_file_csv('L05c1-T188.1-EB/6GHz/NN-L05c1-T188.1-EB-6G')
##input_file_csv('L05c1-T188.1-EB/6GHz/NS-L05c1-T188.1-EB-6G')
##input_file_csv('L05c1-T188.1-EB/6GHz/SN-L05c1-T188.1-EB-6G')
##input_file_csv('L05c1-T188.1-EB/6GHz/SS-L05c1-T188.1-EB-6G')

##input_file_csv('L05c1-T188.1-EC/1GHz/NN-L05c1-T188.1-EC-1G')
##input_file_csv('L05c1-T188.1-EC/1GHz/NS-L05c1-T188.1-EC-1G')
##input_file_csv('L05c1-T188.1-EC/1GHz/SN-L05c1-T188.1-EC-1G')
##input_file_csv('L05c1-T188.1-EC/1GHz/SS-L05c1-T188.1-EC-1G')
##input_file_csv('L05c1-T188.1-EC/6GHz/NN-L05c1-T188.1-EC-6G')
##input_file_csv('L05c1-T188.1-EC/6GHz/NS-L05c1-T188.1-EC-6G')
##input_file_csv('L05c1-T188.1-EC/6GHz/SN-L05c1-T188.1-EC-6G')
##input_file_csv('L05c1-T188.1-EC/6GHz/SS-L05c1-T188.1-EC-6G')

#input_file_csv('L05c1-T188.1-ED/1GHz/NN-L05c1-T188.1-ED-1G')
##input_file_csv('L05c1-T188.1-ED/1GHz/NS-L05c1-T188.1-ED-1G')
##input_file_csv('L05c1-T188.1-ED/1GHz/SN-L05c1-T188.1-ED-1G')
##input_file_csv('L05c1-T188.1-ED/1GHz/SS-L05c1-T188.1-ED-1G')
##input_file_csv('L05c1-T188.1-ED/6GHz/NN-L05c1-T188.1-ED-6G')
##input_file_csv('L05c1-T188.1-ED/6GHz/NS-L05c1-T188.1-ED-6G')
##input_file_csv('L05c1-T188.1-ED/6GHz/SN-L05c1-T188.1-ED-6G')
##input_file_csv('L05c1-T188.1-ED/6GHz/SS-L05c1-T188.1-ED-6G')

#input_file_csv('L05c1-T189.1-EA/1GHz/NN-L05c1-T189.1-EA-1G')
##input_file_csv('L05c1-T189.1-EA/6GHz/NN-L05c1-T189.1-EA-6G')

#input_file_csv('L05c1-T189.1-EB/1GHz/NN-L05c1-T189.1-EB-1G')
##input_file_csv('L05c1-T189.1-EB/1GHz/NS-L05c1-T189.1-EB-1G')
##input_file_csv('L05c1-T189.1-EB/1GHz/SN-L05c1-T189.1-EB-1G')
##input_file_csv('L05c1-T189.1-EB/1GHz/SS-L05c1-T189.1-EB-1G')
##input_file_csv('L05c1-T189.1-EB/6GHz/NN-L05c1-T189.1-EB-6G')
##input_file_csv('L05c1-T189.1-EB/6GHz/NS-L05c1-T189.1-EB-6G')
##input_file_csv('L05c1-T189.1-EB/6GHz/SN-L05c1-T189.1-EB-6G')
##input_file_csv('L05c1-T189.1-EB/6GHz/SS-L05c1-T189.1-EB-6G')

#input_file_csv('L05c1-T189.1-EC/1GHz/NN-L05c1-T189.1-EC-1G')
##input_file_csv('L05c1-T189.1-EC/1GHz/NS-L05c1-T189.1-EC-1G')
##input_file_csv('L05c1-T189.1-EC/1GHz/SN-L05c1-T189.1-EC-1G')
##input_file_csv('L05c1-T189.1-EC/1GHz/SS-L05c1-T189.1-EC-1G')
##input_file_csv('L05c1-T189.1-EC/6GHz/NN-L05c1-T189.1-EC-6G')
##input_file_csv('L05c1-T189.1-EC/6GHz/NS-L05c1-T189.1-EC-6G')
##input_file_csv('L05c1-T189.1-EC/6GHz/SN-L05c1-T189.1-EC-6G')
##input_file_csv('L05c1-T189.1-EC/6GHz/SS-L05c1-T189.1-EC-6G')

#input_file_csv('L05c1-T189.1-ED/1GHz/NN-L05c1-T189.1-ED-1G')
##input_file_csv('L05c1-T189.1-ED/1GHz/NS-L05c1-T189.1-ED-1G')
##input_file_csv('L05c1-T189.1-ED/1GHz/SN-L05c1-T189.1-ED-1G')
##input_file_csv('L05c1-T189.1-ED/1GHz/SS-L05c1-T189.1-ED-1G')
##input_file_csv('L05c1-T189.1-ED/6GHz/NN-L05c1-T189.1-ED-6G')
##input_file_csv('L05c1-T189.1-ED/6GHz/NS-L05c1-T189.1-ED-6G')
##input_file_csv('L05c1-T189.1-ED/6GHz/SN-L05c1-T189.1-ED-6G')
##input_file_csv('L05c1-T189.1-ED/6GHz/SS-L05c1-T189.1-ED-6G')
##
#input_file_csv('L05c1-T197.2-EB/1GHz/NN-L05c1-T197.2-EB-1G')
##input_file_csv('L05c1-T197.2-EB/6GHz/NN-L05c1-T197.2-EB-6G')
##
#input_file_csv('L05c1-T197.2-EC/1GHz/NN-L05c1-T197.2-EC-1G')
##input_file_csv('L05c1-T197.2-EC/1GHz/NS-L05c1-T197.2-EC-1G')
##input_file_csv('L05c1-T197.2-EC/1GHz/SN-L05c1-T197.2-EC-1G')
##input_file_csv('L05c1-T197.2-EC/1GHz/SS-L05c1-T197.2-EC-1G')
##input_file_csv('L05c1-T197.2-EC/6GHz/NN-L05c1-T197.2-EC-6G')
##input_file_csv('L05c1-T197.2-EC/6GHz/NS-L05c1-T197.2-EC-6G')
##input_file_csv('L05c1-T197.2-EC/6GHz/SN-L05c1-T197.2-EC-6G')
##input_file_csv('L05c1-T197.2-EC/6GHz/SS-L05c1-T197.2-EC-6G')
##
#input_file_csv('L05c1-T205.1-EA/1GHz/NN-L05c1-T205.1-EA-1G')
##input_file_csv('L05c1-T205.1-EA/1GHz/NS-L05c1-T205.1-EA-1G')
##input_file_csv('L05c1-T205.1-EA/1GHz/SN-L05c1-T205.1-EA-1G')
##input_file_csv('L05c1-T205.1-EA/1GHz/SS-L05c1-T205.1-EA-1G')
##input_file_csv('L05c1-T205.1-EA/6GHz/NN-L05c1-T205.1-EA-6G')
##input_file_csv('L05c1-T205.1-EA/6GHz/NS-L05c1-T205.1-EA-6G')
##input_file_csv('L05c1-T205.1-EA/6GHz/SN-L05c1-T205.1-EA-6G')
##input_file_csv('L05c1-T205.1-EA/6GHz/SS-L05c1-T205.1-EA-6G')
##
input_file_csv('L05c1-T205.1-EB/1GHz/NN-L05c1-T205.1-EB-1G')
##input_file_csv('L05c1-T205.1-EB/1GHz/NS-L05c1-T205.1-EB-1G')
##input_file_csv('L05c1-T205.1-EB/1GHz/SN-L05c1-T205.1-EB-1G')
##input_file_csv('L05c1-T205.1-EB/1GHz/SS-L05c1-T205.1-EB-1G')
##input_file_csv('L05c1-T205.1-EB/6GHz/NN-L05c1-T205.1-EB-6G')
##input_file_csv('L05c1-T205.1-EB/6GHz/NS-L05c1-T205.1-EB-6G')
##input_file_csv('L05c1-T205.1-EB/6GHz/SN-L05c1-T205.1-EB-6G')
##input_file_csv('L05c1-T205.1-EB/6GHz/SS-L05c1-T205.1-EB-6G')
##
#input_file_csv('L05c1-T205.1-EC/1GHz/NN-L05c1-T205.1-EC-1G')
##input_file_csv('L05c1-T205.1-EC/1GHz/NS-L05c1-T205.1-EC-1G')
##input_file_csv('L05c1-T205.1-EC/1GHz/SN-L05c1-T205.1-EC-1G')
##input_file_csv('L05c1-T205.1-EC/1GHz/SS-L05c1-T205.1-EC-1G')
##input_file_csv('L05c1-T205.1-EC/6GHz/NN-L05c1-T205.1-EC-6G')
##input_file_csv('L05c1-T205.1-EC/6GHz/NS-L05c1-T205.1-EC-6G')
##input_file_csv('L05c1-T205.1-EC/6GHz/SN-L05c1-T205.1-EC-6G')
##input_file_csv('L05c1-T205.1-EC/6GHz/SS-L05c1-T205.1-EC-6G')
##
#input_file_csv('L05c1-T205.1-ED/1GHz/NN-L05c1-T205.1-ED-1G')
##input_file_csv('L05c1-T205.1-ED/1GHz/NS-L05c1-T205.1-ED-1G')
##input_file_csv('L05c1-T205.1-ED/1GHz/SN-L05c1-T205.1-ED-1G')
##input_file_csv('L05c1-T205.1-ED/1GHz/SS-L05c1-T205.1-ED-1G')
##input_file_csv('L05c1-T205.1-ED/6GHz/NN-L05c1-T205.1-ED-6G')
##input_file_csv('L05c1-T205.1-ED/6GHz/NS-L05c1-T205.1-ED-6G')
##input_file_csv('L05c1-T205.1-ED/6GHz/SN-L05c1-T205.1-ED-6G')
##input_file_csv('L05c1-T205.1-ED/6GHz/SS-L05c1-T205.1-ED-6G')


plt.xlabel('Frequencies (GHz)')
#plt.ylabel('MLOGarithmic (dB)')
#plt.ylabel('PHASe (Degrees)')
#plt.ylabel('SWR (dB)')
#plt.ylabel('Resistance (Ω)')
plt.ylabel('Reactance (Ω)')

plt.legend(loc=1, prop={'size': 10})
plt.show()

