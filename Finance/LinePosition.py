from sympy import symbols, Eq, solve

def my_replace(x):
    return str(x).replace('.',',')

def apply(a, b, x):
    a = float(a.replace(',','.'))
    b = float(b.replace(',','.'))
    print(round(a*x + b, 2), x)

def get_m():    

    # defining symbols used in equations 
    # or unknown variables 
    a, b = symbols('a,b') 

    # defining equations 
    eq1 = Eq((178*a + b), 77.69) 
    print("Equation 1:") 
    print(eq1) 
    eq2 = Eq((152*a + b), 79.12) 
    print("Equation 2") 
    print(eq2) 

    # solving the equation 
    print("Values of 2 unknown variable are as follows:") 

    x = solve((eq1, eq2), (a, b))
    print(my_replace(x[a]),my_replace(x[b]))

def calculate():
    n = 8
    m = -0.17 # - to decrease

    x1 = 697
    x2 = 792

    y1 = 74.14
    y2 = 74.48

    a, b = symbols('a,b') 

    eq1 = Eq((x1*a + b), y1) 
    eq2 = Eq((x2*a + b), y2) 

    x = solve((eq1, eq2), (a, b))

    a_ = x[a]
    b_ = x[b]

    print('Values of the points are:')

    print( a_ * x1 + (n - 1) * m + b_, a_ * x2 + (n - 1) * m + b_)

apply('-0,0550000000000000', '87,4800000000000', 1000)
#get_m()
#calculate()



 
