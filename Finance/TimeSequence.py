import datetime as dt
import pdb

# 27000 7 horas e 30 minutos
# 27900 7 horas e 45 minutos
# 28200 7 horas e 50 minutos
# 28500 7 horas e 55 minutos
# 28800 8 horas

start = '10:00'
period = 5
module = 27000

def fibonnaci(x):
    if x == 0 or x == 1:
        return 1
    else:
        return fibonnaci(x - 1) + fibonnaci(x - 2)

def calculate(date, j):
    date = dt.datetime.strptime(date, '%H:%M')
    norm = dt.datetime.strptime(start, '%H:%M')
    date1 = date + dt.timedelta(minutes=period*j)
    diff = (date1 - norm).seconds 
    mod = diff % module
    date1 = norm + dt.timedelta(hours=mod // 3600)
    date1 += dt.timedelta(minutes=((mod/3600) % 1) * 60 )
    return date1

def sequence(date, verbose=True):
    dict = {}
    for i in range(15):
        j = fibonnaci(i)
        date1 = calculate(date, j)
        dict[j] = date1
        if verbose:
            print('{} -> {}'.format(j, date1.strftime('%H:%M')))
    return dict

def levels(date, index1):
    dict = sequence(date, False)
    LEVELS = [0, 0.236, 0.382, 0.5, 0.618, 1, 1.618, 2.618]
    for i in LEVELS:
        k = calculate(date, i*index1)
        print('{} -> {}'.format(i, k.strftime('%H:%M')))

date = '10:30'        
#sequence(date)
levels(date, 55)

 
