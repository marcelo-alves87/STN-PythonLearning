import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

#Valor Inicial
P=1000
#Aporte Mensal (Meta)
M=100
#Aporte Mensal (Real)
MM=[]
#Taxa de Juros Mensal (Meta) (%)
i=8
#Taxa de Juros Mensal (Real) (%)
ii=[]
#Prazo (Meses, Começa em 1)
n=60

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
