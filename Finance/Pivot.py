#Formula:
#Pivot Point (P) = (High + Low + Close) / 3
#Resistance 1 (R1) = 2P - Low
#M1 (Midpoint between Pivot and R1) = (P + R1) / 2 
#Support 1 (S1) = 2P - High
#M2 (Midpoint between Pivot and S1) = (P + S1) / 2
#Resistance 2 (R2) = P + (High - Low)
#Support 2 (S2) = P - (High - Low)
#Resistance (R n > 2) = High + n - 1 x (P - Low)
#Support (S n > 2) = Low - n - 1 x (High - P)


##Common Fibonacci Extension Ratios
##1.272 — Often indicates the first significant extension level beyond the primary trend.
##1.414 — Another extension used for moderate trend continuations.
##1.618 — Known as the “golden ratio,” this is frequently a strong level for trend extensions.
##2.0 — Often used in more volatile markets; can signal further continuation.
##2.618 — Another level based on the golden ratio; this marks a larger extension often seen in highly trending markets.
##3.618 — Indicates an even larger continuation, though less common, used in extreme trends.

# Resistance (Fibonacci Extension/Retraction)=P+(High−Low)×1.272
# Support (1.272)=Low−(High−Low)×1.272

HIGH = 96.35
LOW = 93.88
CLOSE = 94.5

EXTENSIONS = [ 1.272, 1.414, 1.618, 2.0, 2.618 ]
RETRACTIONS = [0.236, 0.382, 0.5, 0.618, 0.786 ]

pivot = ( HIGH + LOW + CLOSE ) / 3

print('Pivot Point (P): {}'.format(round(pivot,2)))

for i in range(3):

    if i == 1:

        ri = 2*pivot - LOW
        si = 2*pivot - HIGH
        
        print('Resistance 1 (R1): {}'.format(round(ri,2)))
        print('Midpoint 1 (M1): {}'.format(round((pivot + ri)/2,2)))
        print('Support 1 (S1): {}'.format(round(si,2)))
        print('Midpoint 2 (M2): {}'.format(round((pivot + si)/2,2)))

    if i == 2:

        rj = pivot + (HIGH - LOW)
        sj = pivot - (HIGH - LOW)
        
        print('Resistance 2 (R2): {}'.format(round(rj,2)))
        print('Midpoint 3 (M3): {}'.format(round((ri + rj)/2,2)))
        print('Support 2 (S2): {}'.format(round(sj,2)))
        print('Midpoint 4 (M3): {}'.format(round((si + sj)/2,2)))
    
    if i > 2:

        ri = rj
        si = sj

        rj = HIGH + (i - 1)*(pivot - LOW)
        sj = LOW - (i - 1)*(HIGH - pivot)  

        print('Resistance '+ str(i) +' (R' + str(i) +'): {}'.format(round(rj,2)))
        print('Midpoint '+ str(i + 2) +' (M' + str(i + 2) +'): {}'.format(round((ri + rj)/2,2)))
        print('Support '+ str(i) + ' (S' + str(i) +'): {}'.format(round(sj,2)))
        print('Midpoint '+ str(i + 3) +' (M' + str(i + 3) +'): {}'.format(round((si + sj)/2,2)))

##for i in range(len(EXTENSIONS)):
##
##    print('Fibonacci Resistance '+ str(i) +' (' + str(EXTENSIONS[i]) +'): {}'.format(round(pivot + (HIGH - LOW) * EXTENSIONS[i],2)))
##    print('Fibonacci  Support '+ str(i) + ' (' + str(RETRACTIONS[i]) +'): {}'.format(round(LOW - (HIGH - LOW) * RETRACTIONS[i],2)))
##    
