"""
This is a toy sample
"""

def f1(p1, p2="cherry"):
    # Metodo inefficiente
    result = ""
    for i in range(5):
        result += "Python" + str(i) + " "
    print(result)

    return None


def f2():
    f1(2)  # call to f1
    # Concatenazione di stringhe con il ciclo for e funzione f (supportata solo da 3-6 in su)
    result = ""
    for i in range(5):
        result += "Numero:"+ str(i)
    print(result)
    return None


def f3(jsonresp):
    f1(3)  # call to f1
    
    for lkey in jsonresp:
        for key in lkey:
            print(key, ":", lkey[key])
    for i in range(len(jsonresp)):
        print(i)
        
    return "A string"
    
def f4(test):
    for i in range(10):
        print(i)
        for j in range(5):
            print(j)
        while k < 10:
            k += 1
        while k < 10:
            for t in range(1,10):
                print(t)
                
def f5(test):
    for i in range(5):
        print("Numero " + str(i))

    while True:
        print("Ciao", "Mondo")