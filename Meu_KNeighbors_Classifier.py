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

file = 'data/STN_DATA_DESGASTE_MEDIA.csv'
normalize_csv(file)
df = pd.read_csv(file)
df.replace('?', -99999, inplace=True)
df.drop(['id'], 1, inplace=True)
full_data = df.astype(float).values.tolist()

test_size = 0.2
train_set = {1:[],2:[]}
test_set = {1:[],2:[]}

train_data = full_data[:-int(test_size*len(full_data))]
test_data = full_data[-int(test_size*len(full_data)):]

for i in train_data:
    train_set[i[-1]].append(i[:-1])

for i in test_data:
    test_set[i[-1]].append(i[:-1])

correct = 0
total = 0

for group in test_set:
    for data in test_set[group]:
        vote, confidence = k_nearest_neighbors(train_set, data, k=5)
        if group == vote:
            correct += 1
        else:
            print('(',group, vote,')',' = ',confidence)
            
        total += 1

print('Accuracy:', correct/total)        
            
