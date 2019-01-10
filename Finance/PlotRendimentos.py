import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

#Valor Inicial
P=0
#Aporte Mensal (Meta)
M=500
#Aporte Mensal (Real)
MM=[]
#Taxa de Juros Mensal (Meta) (%)
i=9
#Taxa de Juros Mensal (Real) (%)
ii=[]
#Prazo (Meses, Começa em 1)
n=60

i = i / 100
[x/100 for x in ii]

def get_juros_compostos(n,m,i):
    #http://fazaconta.com/valor-futuro-investimentos.htm
    n+=1
    if n == 1:
        return m
    else:
        return P*(1 + i)**n + m*(((1 + i)**n - 1)/i)

def plotar_grafico_por_meses(aportes, juros):
    for j in range(n):
        y = get_juros_compostos(j,aportes[j],juros[j])
        w = (n * aportes[j] + P)
        if j == n - 1:
            text = ('Total Poupado R$ {}\nJuros Recebidos R$ {}'
                     + '\nMontante Final R$ {}\n\n\n\n').format(w,y - w,y)
            print(text)             
            plt.text(0.02, 0.5,text)
        plt.scatter(j + 1,y)

def plotar_grafico():
    x = n - len(MM)
    aportes = MM + x*[M]
    juros = ii + x*[i]
    plotar_grafico_por_meses(aportes, juros)

def validar_parametros():
    x = len(MM)
    y = len(ii)
    assert x == y,"O tamanho da lista de Aportes e Juros são diferentes"
    assert n >= x,"O prazo em meses é menor que a lista de Aportes Mensais"
    
validar_parametros()
plotar_grafico()
plt.show()
