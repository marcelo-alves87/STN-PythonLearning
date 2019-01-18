import numpy as np
from mpl_toolkits.mplot3d import axes3d
from smithplot import SmithAxes
import matplotlib.pyplot as plt
import pickle
from numpy.fft import fft, fftfreq, ifft

#Haste T189.1-EC
pickle_in = open('T189.1-EC.pickle', 'rb')
y_1891_EC = pickle.load(pickle_in)

#Haste T189.1-EA
pickle_in = open('T189.1-EA.pickle', 'rb')
y_1891_EA = pickle.load(pickle_in)

#Haste T189.1-EB
pickle_in = open('T189.1-EB.pickle', 'rb')
y_1891_EB = pickle.load(pickle_in)

#Haste T189.1-ED
pickle_in = open('T189.1-ED.pickle', 'rb')
y_1891_ED = pickle.load(pickle_in)

#Haste T205.1-EA
pickle_in = open('T205.1-EA.pickle', 'rb')
y_2051_EA = pickle.load(pickle_in)

#Haste T205.1-EB
pickle_in = open('T205.1-EB.pickle', 'rb')
y_2051_EB = pickle.load(pickle_in)

n = 1001
freqs = np.linspace(0.002, 1, n)
x = 1/freqs


y_1891_EB_i = ifft(y_1891_EB)
y_1891_EC_i = ifft(y_1891_EC)
y_1891_ED_i = ifft(y_1891_ED)


y_2051_EA_i = ifft(y_2051_EA)
y_2051_EB_i = ifft(y_2051_EB)

ax = plt.subplot(111, projection='smith')
plt.plot(50*y_1891_EC_i, y_2051_EB,datatype=SmithAxes.Z_PARAMETER)
plt.show()
