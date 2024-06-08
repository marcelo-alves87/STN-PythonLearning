# importing library sympy 
from sympy import symbols, Eq, solve

n = 4
m = -0.17 # - to decrease

x1 = 677
x2 = 790

y1 = 74.09
y2 = 74.51

def my_replace(x):
    return str(x).replace('.',',')

a, b = symbols('a,b') 

eq1 = Eq((x1*a + b), y1) 
eq2 = Eq((x2*a + b), y2) 

x = solve((eq1, eq2), (a, b))

a_ = x[a]
b_ = x[b]

print('Values of the points are:')

print( a_ * x1 + (n - 1) * m + b_, a_ * x2 + (n - 1) * m + b_)

### importing library sympy 
##from sympy import symbols, Eq, solve
##
##def my_replace(x):
##    return str(x).replace('.',',')
##
### defining symbols used in equations 
### or unknown variables 
##a, b = symbols('a,b') 
##
### defining equations 
##eq1 = Eq((120*a + b), 78.48) 
##print("Equation 1:") 
##print(eq1) 
##eq2 = Eq((179*a + b), 79.28) 
##print("Equation 2") 
##print(eq2) 
##
### solving the equation 
##print("Values of 2 unknown variable are as follows:") 
##
##x = solve((eq1, eq2), (a, b))
##print(my_replace(x[a]),my_replace(x[b])) 
