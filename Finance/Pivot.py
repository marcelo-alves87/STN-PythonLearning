#Formula:
#Pivot Point (P) = (High + Low + Close) / 3
#Resistance 1 (R1) = 2P - Low
#Support 1 (S1) = 2P - High
#Resistance 2 (R2) = P + (High - Low)
#Support 2 (S2) = P - (High - Low)
#Resistance (R n > 2) = High + n - 1 x (P - Low)
#Support (S n > 2) = Low - n - 1 x (High - P)


HIGH = 90.87
LOW = 89.21
CLOSE = 90.41
MAX_LEVEL = 4 


pivot = ( HIGH + LOW + CLOSE ) / 3

print('Pivot Point (P): {}'.format(round(pivot,2)))

for i in range(MAX_LEVEL + 1):

    if i == 1:

        print('Resistance 1 (R1): {}'.format(round(2*pivot - LOW,2)))
        print('Support 1 (S1): {}'.format(round(2*pivot - HIGH,2)))

    if i == 2:

        print('Resistance 2 (R2): {}'.format(round(pivot + (HIGH - LOW),2)))
        print('Support 2 (S2): {}'.format(round(pivot - (HIGH - LOW),2)))
    
    if i > 2:

        print('Resistance '+ str(i) +' (R' + str(i) +'): {}'.format(round(HIGH + (i - 1)*(pivot - LOW),2)))
        print('Support '+ str(i) + ' (S' + str(i) +'): {}'.format(round(LOW - (i - 1)*(HIGH - pivot),2)))
