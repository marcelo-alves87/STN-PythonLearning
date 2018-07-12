import numpy as np
from sklearn import preprocessing, cross_validation, neighbors
import pandas as pd
import pickle


number_of_predictions = range(5, 25)

def input_file_csv(filename, clazz):
    normalize_csv(filename)
    df = pd.read_csv(filename, low_memory=False)
    df.replace('?', -99999, inplace=True)
    df.fillna(-99999, inplace=True)
    df.drop(['id'], 1, inplace=True)
    X = np.array(df).T
    y = np.full(len(X), clazz, dtype=np.float64)
    return X, y

def normalize_csv(filename):

    fileread = open(filename).read()    
    needToNorm = True

    if 'id,' in fileread:
        needToNorm = False
       
    if needToNorm:
        newtext=fileread.replace(',','.')
        newtext=newtext.replace(';',',')

        with open(filename, "w") as f:
            f.write(newtext)

def append_array(filename, clazz):
    global X
    global y

    X1, y1 = input_file_csv(filename, clazz)
    y = np.append(y, y1)
    X = np.append(X, X1, axis=0)
    
X, y = input_file_csv('medidas/desgaste/H1N_FASE_2.csv', 1)
append_array('medidas/desgaste/H1D10.csv', 2)
append_array('medidas/desgaste/H1D15_FASE_2.csv', 2)
append_array('medidas/desgaste/H1D25.csv', 2)
append_array('medidas/desgaste/H1D30-20.csv', 2)
append_array('medidas/desgaste/H1D50-20.csv', 2)
append_array('medidas/desgaste/H1D65.csv', 2)
append_array('medidas/desgaste/H1D75.csv', 2)
append_array('medidas/desgaste/H1D80.csv', 2)

Z = np.c_[X.reshape(len(X), -1), y.reshape(len(y), -1)]    
np.random.shuffle(Z)

X = np.delete(Z, -1, axis=1)
y = Z[:,-1]

X_predict = X[number_of_predictions]
X = np.delete(X, number_of_predictions, axis=0)

y_predict = y[number_of_predictions]
y = np.delete(y, number_of_predictions, axis=0)

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

clf = neighbors.KNeighborsClassifier()
clf.fit(X_train, y_train)

with open('neighborsclassifier.pickle', 'wb') as f:
    pickle.dump(clf, f)

pickle_in = open('neighborsclassifier.pickle', 'rb')
clf = pickle.load(pickle_in)    

accuracy = clf.score(X_test, y_test)
print(accuracy)

print(clf.predict(X_predict))
print(y_predict)
