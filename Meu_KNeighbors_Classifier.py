import numpy as np
import pandas as pd
import random
import warnings
from collections import Counter

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

def k_nearest_neighbors(data, predict, k=3):
    if len(data) >= k:
        warnings.warn('K is set to a value less than total voting groups!')
    distances = []
    for group in data:
        for features in data[group]:
            euclidean_distance = np.linalg.norm(np.array(features)-np.array(predict))
            distances.append([euclidean_distance, group])
    votes = [i[1] for i in sorted(distances)[:k]]
    vote_result = Counter(votes).most_common(1)[0][0]
    confidence = Counter(votes).most_common(1)[0][1] / k
    return vote_result, confidence

def append(dictionary, clazz, data, times):
    for i in range(times):
        dictionary[clazz].append(data)

def append_if(dictionary, clazz, data, uniform):
    x = random.uniform(0, 1)
    if x < uniform:
        dictionary[clazz].append(data)
        
file = 'data/STN_DATA_DESGASTE_MEDIA.csv'
normalize_csv(file)
df = pd.read_csv(file)
df.replace('?', -99999, inplace=True)
df.drop(['id'], 1, inplace=True)
full_data = df.astype(float).values.tolist()
print('Data length:',len(full_data))

clazz1_len = 0
for i in range(len(full_data)):
    x = full_data[i]
    if(x[-1:][0] == 1):
        clazz1_len+=1
print('Class 1 length:',clazz1_len)
print('Class 2 length:',len(full_data)-clazz1_len)

###Frequency Range###
full_data = np.array(full_data, dtype=np.float64)
x = full_data.T
x = x[:]
x = x.T
y = full_data[:,-1:]
for i in range(len(x)):
    x[i,-1] = y[i]
full_data = x
np.random.shuffle(full_data)
#####################

test_size = 0.1
print('Test length:', test_size)
train_set = {1:[],2:[]}
test_set = {1:[],2:[]}

train_data = full_data[:-int(test_size*len(full_data))]
test_data = full_data[-int(test_size*len(full_data)):]

for i in train_data:
    clazz = i[-1]
    if clazz == 1:
        append(train_set, clazz, i[:-1], 2)
    else:
        append_if(train_set, clazz, i[:-1], 1)

for i in test_data:
    clazz = i[-1]
    if clazz == 1:
        append(test_set, clazz, i[:-1], 1)
    else:
        append_if(test_set, clazz, i[:-1], 1)
        
class1_train = len(train_set[1])
class2_train = len(train_set[2])
all_train = class1_train + class2_train
print('Class distribution in training:',class1_train/all_train,class2_train/all_train)

class1_test = len(test_set[1])
class2_test = len(test_set[2])
all_test = class1_test + class2_test
print('Class distribution in test:',class1_test/all_test,class2_test/all_test)

correct = 0
total = 0

for group in test_set:
    for data in test_set[group]:
        vote, confidence = k_nearest_neighbors(train_set, data, k=5)
        if group == vote:
            correct += 1            
        elif confidence <= 1:
            print('(','Real:',group,' Pred: ', vote,')',' = ',confidence)            
        total += 1

print('Accuracy:', correct/total)        

