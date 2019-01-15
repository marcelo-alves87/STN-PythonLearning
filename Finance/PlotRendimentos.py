import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

#Valor Inicial
P=100
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


def formula_juros(exponencial,juros):
    return (1 + juros/100)**exponencial

def plotar_grafico_por_meses(aportes, juros, periodo=n, rendimentos=0):
    if periodo == 0:
        text = ('Total Poupado R$ {}\nJuros Recebidos R$ {}'
                        + '\nMontante Final R$ {}\n\n\n\n').format(P + sum(aportes),rendimentos - sum(aportes),P + rendimentos)
        plt.text(0.02, 0.5,text)
        print(text)
    else:
        if periodo == n:
            rendimentos += P*formula_juros(n-1,juros[n-1]) + aportes[0]
        else:
            rendimentos += aportes[periodo]*formula_juros(periodo,juros[periodo])
        plt.scatter(n-periodo,rendimentos)
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
