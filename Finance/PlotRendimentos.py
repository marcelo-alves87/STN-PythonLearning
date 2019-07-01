import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

#Valor Inicial
P=500
#Aporte Mensal (Meta)
M=500
#Aporte Mensal (Real)
MM=[]
#Taxa de Juros Mensal (Meta) (%)
i=0.57
#Taxa de Juros Mensal (Real) (%)
ii=[]
#Prazo (Meses, Começa em 1)
n=48

def plotar_grafico_por_meses(aportes, juros, periodo=n, rendimentos=0):
    if periodo == 0:
        text = ('Total Poupado R$ {}\nJuros Recebidos R$ {}'
                        + '\nMontante Final R$ {}\n\n\n\n').format(P + sum(aportes),rendimentos - sum(aportes) - P,rendimentos)
        print(text)
        plt.text(0.02, 0.5,text)
    else:
        if periodo == n:
            rendimentos = (P + aportes[0]) + (P + aportes[0])*juros[0]/100
        else:
            rendimentos = (rendimentos + aportes[periodo]) + (rendimentos + aportes[periodo])*juros[periodo]/100            
        plt.scatter(n-periodo+1,rendimentos)
        plotar_grafico_por_meses(aportes,juros,periodo-1,rendimentos)
      
def plotar_grafico(aportes,juros):
    plotar_grafico_por_meses(aportes, juros)

def validar_parametros(aportes,juros):
    x = len(aportes)
    y = len(juros)
    assert x == y,"O tamanho da lista de Aportes e Juros são diferentes"
    assert n >= x,"O prazo em meses é menor que a lista de Aportes Mensais"

def ajustar_parametros():
    x = n - len(MM)
    y = n - len(ii)
    aportes = MM + x*[M]
    juros = ii + y*[i]
    return aportes,juros

aportes,juros = ajustar_parametros()
validar_parametros(aportes,juros)
plotar_grafico(aportes,juros)
plt.show()
