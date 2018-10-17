# Protótipo STN Rev.A

# Importando bibliotecas
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import keras
from keras.models import Sequential
from keras.layers import Dense

# Importando dados
dataset = pd.read_excel('STN_Rev.Nivel_1.xlsx')
X = dataset.iloc[:,:1001].values
y = dataset.iloc[:, 1001:].values


# Separando dados de treinamento e de teste
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

# Normalizando dados
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Iniciando RNA
classifier = Sequential()

# Hidden Layer #1
classifier.add(Dense(output_dim = 550, init = 'uniform', activation = 'relu', input_dim = 1001))

# Hidden Layer #2
classifier.add(Dense(output_dim = 150, init = 'uniform', activation = 'sigmoid'))

# Hidden Layer #3
classifier.add(Dense(output_dim = 20, init = 'uniform', activation = 'relu'))

# Neurônios de Saída
classifier.add(Dense(output_dim = 4, init = 'uniform', activation = 'sigmoid'))

# Compilando RNA
classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

# Aplicando os dados de treino a RNA
classifier.fit(X_train, y_train, batch_size = 10, nb_epoch = 100)

# Fazendo previsões dos dados de Teste
y_pred = classifier.predict(X_test)
#y_pred = (y_pred > 0.5)
for i in range(88):
    j = 0
    maior_temp = y_pred[i,j]
    maior_j = j
    for j in range(4):
        if (y_pred[i,j] >= maior_temp):
            maior_temp = y_pred[i,j]
            maior_j = j
    for k in range(4):
        y_pred[i,k] = 0
    y_pred[i, maior_j] = 1
            
y_pred_int = np.array(y_pred, dtype=np.int64)

# Calculando Matriz de Confusão
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test.argmax(axis=1), y_pred_int.argmax(axis=1))
diagonal = cm.diagonal()
acertos = diagonal.sum()
total = cm.sum()
Score = acertos/total
print(str(Score))
