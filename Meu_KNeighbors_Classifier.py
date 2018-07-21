import numpy as np
from math import sqrt
import warnings
from collections import Counter
import pandas as pd
import pickle


def k_nearest_neighbors(data, predict, k=2):
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

df = pd.read_csv('data/STN_DATA_DESGASTE_MEDIA.csv')
df.replace('?', -99999, inplace=True)
df.drop(['id'], 1, inplace=True)
full_data = np.array(df, dtype=np.float64)

pickle_in = open('classifier.pickle', 'rb')
train_set = pickle.load(pickle_in)
    
best = 0

np.random.shuffle(full_data)    
test_size = 1
# train_set = {1:[],2:[]}
test_set= {1:[],2:[]}

train_data = full_data[:-int(test_size*len(full_data))]
test_data = full_data[-int(test_size*len(full_data)):]

##    for i in train_data:
##        train_set[i[-1]].append(i[:-1])

for i in test_data:
    test_set[i[-1]].append(i[:-1])

correct = 0
total = 0
confidences=[[]] 


for group in test_set:
    for data in test_set[group]:
        vote, confidence = k_nearest_neighbors(train_set, data)
        if group == vote:
            correct += 1
        else:
            confidences.append([group,vote,confidence])
        total += 1

if correct/total > best:
    best = correct/total
    print(best)
    print(confidences)
##        with open('classifier.pickle', 'wb') as f:
##            pickle.dump(train_set, f)


