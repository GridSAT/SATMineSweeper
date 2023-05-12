from random import randint

def write_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)
def genGrid(name,desc,largeur,hauteur,perC,perS,perT):
    tab = []
    for i in range(hauteur):
        line = []
        for j in range(largeur):
            line.append("-")
        tab.append(line)

    if(perC+perT+perS<90):
        nbC = round(largeur*hauteur*perC/100)
        nbS = round(largeur*hauteur*perS/100)
        nbT = round(largeur*hauteur*perT/100)
    else:
        return
    while nbC > 0:
        i = randint(0,hauteur-1)
        j = randint(0,largeur-1)
        if tab[i][j] == "-":
            if(randint(0,1)):
                tab[i][j] = "C"
            else:
                tab[i][j] = "W"
            nbC-=1
    while nbT > 0:
        i = randint(0,hauteur-1)
        j = randint(0,largeur-1)
        if tab[i][j] == "-":
            tab[i][j] = "T"
            nbT-=1
    while nbS > 0:
        i = randint(0,hauteur-1)
        j = randint(0,largeur-1)
        if tab[i][j] == "-":
            tab[i][j] = "S"
            nbS-=1
    for i in range(hauteur):
        for j in range(largeur):
            if tab[i][j] == "-" and randint(0,1):
                tab[i][j] = "~"
    start = None
    while not start:
        i = randint(1,hauteur-2)
        j = randint(1,largeur-2)
        toAdd=True
        for i2 in range(i-1,i+2):
            for j2 in range(j-1,j+2):
                if tab[i2][j2]!= "-" and tab[i2][j2]!= "~":
                    toAdd=False
        if toAdd:
            start = [i,j]
    string = desc+"\n"+str(hauteur)+" "+str(largeur)+"\n"+str(start[0])+" "+str(start[1])+"\n"
    for i in range(hauteur):
        for j in range(largeur):
            string+=tab[i][j]
            if j < largeur-1:
                string+=" "
        string+="\n"

    write_file(string,name+".croco")

nb = int(input("Nombre de maps : "))
minL = int(input("Largeur min : "))
maxL = int(input("Largeur max : "))
minH = int(input("Hauteur min : "))
maxH = int(input("Hauteur max : "))
minC = int(input("Pourcentage min de Croco : "))
maxC = int(input("Pourcentage max de Croco : "))
minS = int(input("Pourcentage min de Requin : "))
maxS = int(input("Pourcentage max de Requin : "))
minT = int(input("Pourcentage min de Tigre : "))
maxT = int(input("Pourcentage max de Tigre : "))

for i in range(nb):
    genGrid("generated map n"+str(i),"generated map",randint(minL,maxL),randint(minH,maxH),randint(minC,maxC),randint(minS,maxS),randint(minT,maxT))