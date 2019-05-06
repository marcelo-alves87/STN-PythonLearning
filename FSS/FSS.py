import cmath
import numpy as np
import matplotlib.pyplot as plt

#Programa da cruz de Jerusalém
#----------------------------------------------------
# Este programa calcula o coeficiente de reflexão,
# de transmissão, a potência transmitida e refletida
# de uma FSS com células alinhadas
# usando elemento do tipo cruz de Jerusalém
#----------------------------------------------------
# Entrada de dados
#--------------------------------------------------------------

finicial=1 # frequência inicial em GHz
ffinal=25 # frequência final em GHz
df=0.01 # Variação da frequência em GHz
teta=0 # ângulo de incidência teta
p=2.35 # periodocidade da cruz em (cm)
d0=2.05
w=0.1 # largura da fita em (cm)
d=1.61 # tamanho da cruz em (cm)
h=0.1 # largura do braço principal da cruz em (cm)
g=0.05 # largura entre os elementos da estrutura em (cm)
teta=teta*cmath.pi/180 # transforma graus para radianos
nf=((ffinal-finicial)/df)+1 # calcula a quantidade de iterações

def csc(x):
    return 1/cmath.sin(x)

def GG(p,w,lamb,ang):
    b=cmath.sin(cmath.pi*w/(2*p))
    Cp=(1/cmath.sqrt(1+(2*p*cmath.sin(ang)/lamb)-(p*cmath.cos(ang)/lamb)**2))-1
    Cn=(1/cmath.sqrt(1-(2*p*cmath.sin(ang)/lamb)-(p*cmath.cos(ang)/lamb)**2))-1
    num=0.5*((1-b**2)**2)*((1-(b/2)**2)*(Cp+Cn)+4*(b**2)*Cp*Cn)
    den=(1-(b/2)**2)+(b**2)*(1+((b**2)/2)-((b**4)/8))*(Cp+Cn)+2*(b**6)*Cp*Cn
    return num/den

def FF(p,w,lamb,ang):
    return ((p*(cmath.cos(ang)))/lamb)*(cmath.log(csc(cmath.pi*w/(2*p)))+GG(p,w,lamb,ang))

def main(label1,fator_correcao):

    fop = [nf]
    ct = [nf]
    pt = [nf] 
    pr = [nf] 
    ctdb = [nf]
    crdb = [nf]
    cr = [nf]
    
    for ii in range(int(nf)):
        freq=finicial+(ii-1)*df #incrementa a frequência
        lamb=0.49*30/(freq) #calcula o comprimento de onda lambda (em cm)

        #----------------------------- Dipolo cruzado ----------------------------------------

        XL1=FF(p,2*w,lamb,teta) #calcula a reatancia indutiva #1 da cruz
        Bg= ((d)/p)*FF(p,g,lamb,teta) #calcula a susceptância da cruz
        Bd= (4*(2*w+g)/p)*FF(p,p-d,lamb,teta) # calcula a susceptancia da cruz
        BC1=(Bg+Bd).real #calcula a susceptancia da cruz


        #--------------------------- Dipolo da extremidade  ------------------------------------------

        lamb1=d/0.5
        f2=30/lamb1 
        XL3=(d/p)*FF(p,2*h,lamb1,teta)
        BC2=((1/XL3)*((freq/f2)**2)) #A suceptância BC2 é utilizada para suavizar a frequência central f2

        #------------------------- Cálculo das admitâncias ------------------------

        Y1=1/(XL1-(1/BC1))  #Calcula a admitância 1
        Y2=1/(XL3-(1/BC2)) #Calcula a admitância 2
        Yt=Y1+Y2 #Calcula a admitância total da 2ª parte - Langley

        #--------------------- efeito do dieletrico na frequência de corte --------
        
        fop.append(freq/fator_correcao) #armazena a frequência no vetor fop corrigido aparti
        #do valor da permissividade do dieletrico

        #------------------------- Platagem das curvas  ---------------------------

        ct.append(1/cmath.sqrt(1+.25*((Yt)**2))) #calcula e armazena o coeficiente de transmissão no vetor ct (dB)
        pt.append((ct[ii]**2)) #calcula e armazena a potência transmitida no vetor pt
        pr.append(1-ct[ii])  #calcula e armazena a potência refletida no vetor pr
        ctdb_item = 10*cmath.log10( (1/cmath.sqrt(1+.25*((Yt)**2))))
        ctdb.append(ctdb_item)
        crdb.append(20*cmath.log10(1-ct[ii]))
        cr.append(cmath.sqrt(pr[ii])) #calcula e armazena o coeficiente de reflexao no vetor cr

    plt.plot(fop[1:],ctdb[1:],label=label1)

main('No Dielectric Permissivity',1)
main('Dielectric Permissivity',1.5)
plt.xlabel('Freq (GHz)')
plt.ylabel('S21 (dB)')
plt.xticks(np.arange(0,25,1))
plt.grid()
plt.legend()
plt.show()


