import numpy as np
import matplotlib as mpl
#mpl.use('pdf')
import matplotlib.pyplot as plt

plt.rc('font', family='sans')
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')
plt.rc('text', usetex=True)
fig = plt.figure(figsize=(4, 3))
ax = fig.add_subplot(1, 1, 1)

x = np.linspace(1., 8., 30)
ax.plot(x, x ** 1.5, color='k', ls='solid')
ax.plot(x, 20/x, color='0.50', ls='dashed')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Temperature (K)')
plt.show()
