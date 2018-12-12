import numpy as np
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


#x = x[::-1]

#velocidade em 6,33m
x = x[::-1]*0.0958

#velocidade em 8,6m
#x = x[::-1]*0.137

#plt.plot(freqs,y_1891_EB,label='T189.1-EB')
#plt.plot(freqs,y_1891_EC,label='T189.1-EC')
#plt.plot(freqs,y_1891_ED,label='T189.1-ED')

plt.plot(x,y_1891_EB_i,label='T189.1-EB')
plt.plot(x,y_1891_EC_i,label='T189.1-EC')
#plt.plot(x,y_1891_ED_i,label='T189.1-ED')


#plt.plot(x,y_2051_EA_i,label='T205.1-EA')
#plt.plot(x,y_2051_EB_i,label='T205.1-EB')


plt.legend()
plt.xlabel('m')
plt.ylabel('S11')
plt.show()
