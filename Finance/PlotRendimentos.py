import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

#Valor Inicial
P=0
#Aporte Mensal
M=1000
#Taxa de Juros Mensal (%)
i=10
#Prazo (Meses)
n=60

i = i / 100

def get_juros_compostos(n,i):
    return P*(1 + i)**n + M*(((1 + i)**n - 1)/i)

def plotar_grafico_por_meses():
    for j in range(n+1):
        y = get_juros_compostos(j,i)
        w = (n * M + P)
        if j == n:
            plt.text(0.02, 0.5,
                     ('Total Poupado R$ {}\nJuros Recebidos R$ {}'
                     + '\nMontante Final R$ {}\n\n\n\n')
                         .format(w,y - w,y))
            
        plt.scatter(j,get_juros_compostos(j,i))

plotar_grafico_por_meses()
plt.show()
