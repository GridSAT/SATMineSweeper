from typing import *
import subprocess
import fileinput

variable = int
cell = Dict
map = List[List[cell]]
coord = [int,int]
clause = List[variable]
#toVisit= List[coord]

currentMap = None
"""
Créé la map en vide en fonction de la taille

"""
def createMapFromInfo(grid_infos)-> map: 
    dict = {'terrain': None, 'presence': None, 'visited': False,'voisinsTigre':None,'voisinsRequin':None,'voisinsCroco':None}
    map = []
    for i in range(grid_infos["m"]):
        line = []
        for j in range(grid_infos["n"]):
            line.append(dict.copy())
        map.append(line)

    return map


"""
permet de donner la variable 
dimacs en fonction de la position
"""

def toVariable (row:int,col:int,N : int) -> variable:
    return (row * N + col)*3

def toCase (var : variable, N : int)-> coord:
    return var // 7 // N, var // 7 % N

"""
retourne les voisins d'une case 
en fonction de sa position
"""
def getVoisin(i : int,j :int,N,M):
    listeVoisin=[]
    if(i!=0):
        listeVoisin.append([i-1, j])
        if(j!=0):
            listeVoisin.append([i-1, j-1])
        if(j!=(N-1)):
            listeVoisin.append([i-1, j+1])
    if(i!=(M-1)):
        listeVoisin.append([i+1, j])
        if(j!=0):
            listeVoisin.append([i+1, j-1])
        if(j!=(N-1)):
            listeVoisin.append([i+1, j+1])
    if(j!=0):
        listeVoisin.append([i, j-1])
    if(j!=(N-1)):
        listeVoisin.append([i, j+1])
    return listeVoisin


def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)
"""
Recupere les cellulles non visitées
"""
def getLastCell(currentMap,N,M):
    return [[i,j] for i in range(M) for j in range(N) if not currentMap[i][j]["visited"]]
"""
verifie si le chord est possible : tous les animaux 
decouverts et des cases non visitées
"""
def checkChord(map,N,M,i,j):
    notVisited = 0
    nbRequin = 0
    nbTigre = 0
    nbCroco = 0
    for cell in getVoisin(i,j,N,M):
        if(not map[cell[0]][cell[1]]["visited"]):
            notVisited += 1
        if(map[cell[0]][cell[1]]["presence"] == "Requin"):
            nbRequin += 1
        if(map[cell[0]][cell[1]]["presence"] == "Tigre"):
            nbRequin += 1
        if(map[cell[0]][cell[1]]["presence"] == "Croco"):
            nbRequin += 1
    if(notVisited > 0 and nbRequin == map[i][j]["voisinsRequin"] and nbTigre == map[i][j]["voisinsTigre"] and nbCroco == map[i][j]["voisinsCroco"]):
        return True
    else:
        return False




def exec_gophersat(
    filename: str, cmd: str = "gophersat", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False

    model = lines[2][2:].split(" ")
    tab = [int(x) for x in model]
    return True,tab

"""
Retourne la quantité d'animaux non decouverts dans le voisinage 
"""
def getUnsdicoveredEnnemi(i, j, currentMap, N, M):
    if(currentMap[i][j]["voisinsRequin"]==None):
        return 0,0,0
    requin = 0
    tigre = 0
    croc = 0
    for v in getVoisin(i,j,N,M):
        if(currentMap[v[0]][v[1]]["presence"]=="Requin"):
            requin+=1
        elif(currentMap[v[0]][v[1]]["presence"]=="Tigre"):
            tigre+=1
        elif(currentMap[v[0]][v[1]]["presence"]=="Croco"):
            croc+=1
    requinR = currentMap[i][j]["voisinsRequin"] - requin
    tigreR = currentMap[i][j]["voisinsTigre"] - tigre
    crocoR = currentMap[i][j]["voisinsCroco"] - croc
    return requinR, crocoR, tigreR
"""
Verifie si la presence d'un croco est possible 
( si chaque voisin a un croco non decouvert)
"""
def checkCrocoUseful(i,j,currentMap,N,M):
    for v in getVoisin(i,j,N,M):
        if currentMap[v[0]][v[1]]["voisinsCroco"]!=None:
            if currentMap[v[0]][v[1]]["voisinsCroco"] == 0:
                return False
            S,C,T = getUnsdicoveredEnnemi(v[0],v[1],currentMap,N,M)
            if C == 0:
                return False
    return True

def checkTigreUseful(i,j,currentMap,N,M):
    for v in getVoisin(i,j,N,M):

        if currentMap[v[0]][v[1]]["voisinsCroco"]!=None:
            if currentMap[v[0]][v[1]]["voisinsTigre"] == 0:
                return False
            S,C,T = getUnsdicoveredEnnemi(v[0],v[1],currentMap,N,M)
            if T == 0:
                return False
    return True

def checkRequinUseful(i,j,currentMap,N,M):
    for v in getVoisin(i,j,N,M):
        if currentMap[v[0]][v[1]]["voisinsCroco"]!=None:
            if currentMap[v[0]][v[1]]["voisinsRequin"] == 0:
                return False
            S,C,T = getUnsdicoveredEnnemi(v[0],v[1],currentMap,N,M)
            if S == 0:
                return False

    return True
"""
retourne pour une case la probabilité quil y ait un animal specifique
"""
def getProbaUnsdicoveredEnnemi(i,j,currentMap,N,M):
    if(currentMap[i][j]["voisinsRequin"]==None):
        return 0,0,0
    S = 0
    T = 0
    C = 0
    Mer = 0
    Terre = 0
    for v in getVoisin(i,j,N,M):
        if(currentMap[v[0]][v[1]]["presence"]=="Requin"):
            S+=1
        elif(currentMap[v[0]][v[1]]["presence"]=="Tigre"):
            T+=1
        elif(currentMap[v[0]][v[1]]["presence"]=="Croco"):
            C+=1
        if currentMap[v[0]][v[1]]["terrain"]=="land" and currentMap[v[0]][v[1]]["presence"] == None:
            Terre+=1
        elif currentMap[v[0]][v[1]]["terrain"]=="sea" and currentMap[v[0]][v[1]]["presence"] == None:
            Mer+=1
        if(Mer == 0):
            probaS = 0
        else:
            probaS = (currentMap[i][j]["voisinsRequin"]-S)/Mer
        if(Terre == 0):
            probaT = 0
        else:
            probaT = (currentMap[i][j]["voisinsTigre"]-T)/Terre
        if(Terre == 0 and Mer == 0):
            probaC = 0
        else:
            probaC = (currentMap[i][j]["voisinsCroco"]-C)/(Mer+Terre)
    return probaS,probaC,probaT
"""
retourne une approximation de la probabilité d"unanimal sur la case
"""
def getGetProbaCase(i,j,currentMap,N,M):
    val = 0
    for v in getVoisin(i,j,N,M):
        S,C,T = getProbaUnsdicoveredEnnemi(v[0],v[1],currentMap,N,M)
        val += C
        if currentMap[i][j]["terrain"]=="land":
            val+=T
        elif currentMap[i][j]["terrain"]=="sea":
            val+=S
    return val
"""
Test la presence d'un animal sans tout reecrire le dimacs

"""
def testDimacs(clause):
    file = open("test.cnf","rb+")
    file.seek(0,2)
    pos = file.tell()
    file.write(str.encode(clause+"\n"))
    file.close()
    res = exec_gophersat("test.cnf","gophersat-1.1.6.exe")
    file = open("test.cnf","rb+")
    file.seek(pos,0)
    
    file.truncate()
    file.close()
    return not res
"""
Permet de modifier le dimacs sans tout reecrire mais a des problemes 
lorsque l'on passe d'un nombre de clause a n chiffre a un nombre de clauses a n+1 chiffre
"""
def updateDimacs(newClause,size,N,M):
    firstLine= "p cnf "+str(N*M*3)+" "+str(len(newClause)+size+1)
    file = open("test.cnf","rb+")
    file.seek(0,0)
    file.write(str.encode(firstLine+"\n"))
    file.seek(0,2)

    line = ""
    for c in newClause:
        if(c==[-2]):
            raise ValueError("wtf")
        for e in c:
            line+=str(e)+" "
        line+="0\n"
    file.write(str.encode(line))
    file.close()

