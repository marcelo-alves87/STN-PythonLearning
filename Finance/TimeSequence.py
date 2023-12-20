import datetime as dt
import pdb

# 28200 7 horas e 50 minutos
# 28500 7 horas e 55 minutos
# 28800 8 horas

def fibonnaci(x):
    if x == 0 or x == 1:
        return 1
    else:
        return fibonnaci(x - 1) + fibonnaci(x - 2)

date = '15:35' 


date = dt.datetime.strptime(date, '%H:%M')
norm = dt.datetime.strptime('10:05', '%H:%M')

for i in range(15):
    j = fibonnaci(i)
    date1 = date + dt.timedelta(minutes=5*j)
    diff = (date1 - norm).seconds
    mod = diff % 28200
    date1 = norm + dt.timedelta(hours=mod // 3600)
    date1 += dt.timedelta(minutes=((mod/3600) % 1) * 60 )
    print('{} -> {}'.format(j, date1.strftime('%H:%M')))



 
