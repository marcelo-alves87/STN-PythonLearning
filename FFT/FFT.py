#https://www.youtube.com/watch?v=su9YSmwZmPg
import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq,ifft

#number of points
n = 1000

#Period in seconds
T = 100

#angular frequency
w = 2 * np.pi / T
#print('w',w)

#Create n seconds, from 0 to T
x = np.linspace(0, T, n)

#Create individual signals
y1 = 2*np.cos(5*w*x)
y2 = 1*np.sin(10*w*x)
y3 = 0.5*np.sin(20*w*x)

y = y1 + y2 + y3

#Creates necessary frequencies
freqs = fftfreq(n)

#Ignoring negative values
mask = freqs > 0

#FFT
fft_vals = fft(y)

#True theorical fft
fft_theo = 2*np.abs(fft_vals/n)


plt.figure(1)
plt.title('Time Domain Signal')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.plot(x, y)

plt.figure(2)
plt.title('Frequency Domain Signal')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.plot(freqs[mask], fft_theo[mask])

#print(freqs[mask])
##td_values = ifft(fft_vals)
##
##plt.figure(2)
##plt.title('Time Domain Signal')
##plt.xlabel('Time (seconds)')
##plt.ylabel('Amplitude')
##plt.plot(x, td_values)

plt.show()
