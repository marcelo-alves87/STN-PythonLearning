import numpy as np
import matplotlib.pyplot as plt
import pickle
from numpy.fft import fft, fftfreq, ifft

#Haste T176.2-EA
pickle_in = open('T176.2-EA.pickle', 'rb')
y_1762_EA = pickle.load(pickle_in)

#Haste T176.2-EB
pickle_in = open('T176.2-EB.pickle', 'rb')
y_1762_EB = pickle.load(pickle_in)

#Haste T176.2-ED
pickle_in = open('T176.2-ED.pickle', 'rb')
y_1762_ED = pickle.load(pickle_in)

#Haste T188.1-EA
pickle_in = open('T188.1-EA.pickle', 'rb')
y_1881_EA = pickle.load(pickle_in)

#Haste T188.1-EB
pickle_in = open('T188.1-EB.pickle', 'rb')
y_1881_EB = pickle.load(pickle_in)

#Haste T188.1-EC
pickle_in = open('T188.1-EC.pickle', 'rb')
y_1881_EC = pickle.load(pickle_in)

#Haste T188.1-ED
pickle_in = open('T188.1-ED.pickle', 'rb')
y_1881_ED = pickle.load(pickle_in)

#Haste T189.1-EA
pickle_in = open('T189.1-EA.pickle', 'rb')
y_1891_EA = pickle.load(pickle_in)

#Haste T189.1-EB
pickle_in = open('T189.1-EB.pickle', 'rb')
y_1891_EB = pickle.load(pickle_in)

#Haste T189.1-EC
pickle_in = open('T189.1-EC.pickle', 'rb')
y_1891_EC = pickle.load(pickle_in)

#Haste T189.1-ED
pickle_in = open('T189.1-ED.pickle', 'rb')
y_1891_ED = pickle.load(pickle_in)

#Haste T197.2-EB
pickle_in = open('T197.2-EB.pickle', 'rb')
y_1972_EB = pickle.load(pickle_in)

#Haste T197.2-EC
pickle_in = open('T197.2-EC.pickle', 'rb')
y_1972_EC = pickle.load(pickle_in)

#Haste T205.1-EA
pickle_in = open('T205.1-EA.pickle', 'rb')
y_2051_EA = pickle.load(pickle_in)

#Haste T205.1-EB
pickle_in = open('T205.1-EB.pickle', 'rb')
y_2051_EB = pickle.load(pickle_in)

#Haste T205.1-EC
pickle_in = open('T205.1-EC.pickle', 'rb')
y_2051_EC = pickle.load(pickle_in)

#Haste T205.1-ED
pickle_in = open('T205.1-ED.pickle', 'rb')
y_2051_ED = pickle.load(pickle_in)


n = 1001
freqs = np.linspace(0.002, 1, n)
x = 1/freqs


y_1762_EA_i = ifft(y_1762_EA)
y_1762_EB_i = ifft(y_1762_EB)
y_1762_ED_i = ifft(y_1762_ED)

y_1881_EA_i = ifft(y_1881_EA)
y_1881_EB_i = ifft(y_1881_EB)
y_1881_EC_i = ifft(y_1881_EC)
y_1881_ED_i = ifft(y_1881_ED)

y_1891_EB_i = ifft(y_1891_EB)
y_1891_EC_i = ifft(y_1891_EC)
y_1891_ED_i = ifft(y_1891_ED)

y_1972_EB_i = ifft(y_1972_EB)
y_1972_EC_i = ifft(y_1972_EC)

y_2051_EA_i = ifft(y_2051_EA)
y_2051_EB_i = ifft(y_2051_EB)
y_2051_EC_i = ifft(y_2051_EC)
y_2051_ED_i = ifft(y_2051_ED)


x = x[::-1]

#velocidade em 6,33m
#x = x[::-1]*0.0958

#velocidade em 8,6m
#x = x[::-1]*0.137

#plt.plot(freqs,y_1891_EB,label='T189.1-EB')
#plt.plot(freqs,y_1891_EC,label='T189.1-EC')
#plt.plot(freqs,y_1891_ED,label='T189.1-ED')

sort = np.argsort(-y_1762_EA_i)
print('T176.2-EA', x[sort[1]])
sort = np.argsort(-y_1762_EB_i)
print('T176.2-EB', x[sort[1]])
sort = np.argsort(-y_1762_ED_i)
print('T176.2-ED', x[sort[1]])

plt.plot(x,y_1881_EA_i,label='T188.1-EA')
sort = np.argsort(-y_1881_EA_i)
print('T188.1-EA', x[sort[1]])
sort = np.argsort(-y_1881_EB_i)
print('T188.1-EB', x[sort[1]])
sort = np.argsort(-y_1881_EC_i)
print('T188.1-EC', x[sort[1]])
sort = np.argsort(-y_1881_ED_i)
print('T188.1-ED', x[sort[1]])

plt.plot(x,y_1891_EB_i,label='T189.1-EB')
#Get 2nd higher value which is the final transiction
#O tempo que o sinal leva para pecorrer a haste 
sort = np.argsort(-y_1891_EB_i)
print('T189.1-EB', x[sort[1]])

#plt.plot(x,y_1891_EC_i,label='T189.1-EC')
sort = np.argsort(-y_1891_EC_i)
print('T189.1-EC', x[sort[1]])

#plt.plot(x,y_1891_ED_i,label='T189.1-ED')
sort = np.argsort(-y_1891_ED_i)
print('T189.1-ED', x[sort[1]])

sort = np.argsort(-y_1972_EB_i)
print('T197.2-EB', x[sort[1]])
sort = np.argsort(-y_1972_EC_i)
print('T197.2-EC', x[sort[1]])

#plt.plot(x,y_2051_EA_i,label='T205.1-EA')
sort = np.argsort(-y_2051_EA_i)
print('T205.1-EA', x[sort[1]])
#plt.plot(x,y_2051_EB_i,label='T205.1-EB')
sort = np.argsort(-y_2051_EB_i)
print('T205.1-EB', x[sort[1]])
sort = np.argsort(-y_2051_EC_i)
print('T205.1-EC', x[sort[1]])
sort = np.argsort(-y_2051_ED_i)
print('T205.1-ED', x[sort[1]])


plt.legend()
plt.xlabel('ns')
plt.ylabel('S11')
plt.show()
