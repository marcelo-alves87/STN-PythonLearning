import datetime as dt
import pdb

def fibonnaci(x):
    if x == 0 or x == 1:
        return 1
    else:
        return fibonnaci(x - 1) + fibonnaci(x - 2)

def calculate(date, j):
    date1 = date + dt.timedelta(weeks=j//5)
    date1 += dt.timedelta(days=j%5)
    return date1

def sequence(date, verbose=True):
    dict = {}
    date = dt.datetime.strptime(date, '%Y-%m-%d')
    for i in range(15):
        j = fibonnaci(i)
        date1 = calculate(date, j)
       
        dict[j] = date1
        if verbose:
            print('{} -> {}'.format(j, date1.strftime('%Y-%m-%d')))
    return dict

def levels(date, index1):
    dict = sequence(date, False)
    date = dt.datetime.strptime(date, '%Y-%m-%d')
    LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 1, 1.618, 2.618]
    for i in LEVELS:
        k = calculate(date, i*index1)
        print('{} -> {}'.format(i, k.strftime('%Y-%m-%d')))

date = '2024-01-05'        
#sequence(date)
levels(date, 55)


