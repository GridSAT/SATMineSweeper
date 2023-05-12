from typing import *
from itertools import *
from fun import *
from math import *
"""
Si requin alors pas croco etc...
"""
def clauseUniqueTigreRequin(N :int,M:int) -> List[clause]:
    return [[-(toVariable(i,j,N)+3),-(toVariable(i,j,N)+1)] for i in range(M) for j in range(N)]

def clauseUniqueTigreCroco(N :int,M:int) -> List[clause]:
    return [[-(toVariable(i,j,N)+3),-(toVariable(i,j,N)+2)] for i in range(M) for j in range(N)]

def clauseUniqueRequinCroco(N :int,M:int) -> List[clause]:
    return [[-(toVariable(i,j,N)+1),-(toVariable(i,j,N)+2)] for i in range(M) for j in range(N)]



# type = 0,1,2 requin croco tigre
"""
Genere les clause de k animaux parmis les voisins 
en utilisant les combinaisons
retourne [] si trop de clause sont generée
"""
def clauseNbVoisins(voisins, nb : int, type : int, N : int):
    listClause = []
    listVarVoisin = []

    for c in voisins:

        listVarVoisin.append(toVariable(c[0],c[1],N))

    if(comb(len(listVarVoisin), nb)>10000 or comb(len(listVarVoisin), len(voisins)-nb)>10000):
        return []
    listCombinations = list(combinations(listVarVoisin,nb))

    for c in listCombinations:
        clause = []

        for elem in c:
            
            clause.append(-(elem+type + 1))

        for var in listVarVoisin:
            if var not in c:
                copy = clause.copy()
                copy.append(-(var+type + 1))
                listClause.append(copy)

    listCombinations = list(combinations(listVarVoisin,len(voisins)-nb))

    for c in listCombinations:
        clause = []
        for elem in c:
            clause.append(elem+type+1)
        for var in listVarVoisin:
            if var not in c:
                copy = clause.copy()
                copy.append(var+type+1)
                listClause.append(copy)

    return listClause

"""

parcours la maps et encode les clauses
/!\deprecated/!\

"""

def encodeMap(map) :
    listClause=[]
    N = len(map[0])
    M = len(map)
    for i in range(M):
        for j in range(N):
            if map[i][j]['terrain'] == 'sea':
                listClause.append([-(toVariable(i,j,N)+3)])
            elif map[i][j]['terrain'] == 'land':
                listClause.append([-toVariable(i,j,N)-1])
            if map[i][j]['presence'] == "Nothing":
                listClause.append([-toVariable(i,j,N)-1])
                listClause.append([-toVariable(i,j,N)-2])
                listClause.append([-toVariable(i,j,N)-3])
                #print("chelou",toVariable(i,j,N)+7)
            elif map[i][j]['presence'] == "Requin":
                listClause.append([toVariable(i,j,N)+1])
            elif map[i][j]['presence'] == "Tigre":
                listClause.append([toVariable(i,j,N)+3])
            elif map[i][j]['presence'] == "Croco":
                listClause.append([toVariable(i,j,N)+2])

            if map[i][j]['voisinsTigre'] is not None:
                listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsTigre'],2,N)
            if map[i][j]['voisinsCroco'] is not None:
                listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsCroco'],1,N)
            if map[i][j]['voisinsRequin'] is not None:
                listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsRequin'],0,N)

    return listClause
"""
Encode les clauses pour une cellule donnée
3 variables par cellule
1 : requin, 2 : croco, 3:tigre
mer -> non tigre donc -3
terre -> non requin donc -1

"""
def encodeCell(i,j,N,M,map):
    listClause = []
    if map[i][j]['terrain'] == 'sea':
        listClause.append([-toVariable(i,j,N)-3])
    elif map[i][j]['terrain'] == 'land':
        listClause.append([-toVariable(i,j,N)-1])
    if map[i][j]['presence'] == "Nothing":
        listClause.append([-toVariable(i,j,N)-1])
        listClause.append([-toVariable(i,j,N)-2])
        listClause.append([-toVariable(i,j,N)-3])
    elif map[i][j]['presence'] == "Requin":
        listClause.append([toVariable(i,j,N)+1])
    elif map[i][j]['presence'] == "Tigre":
        listClause.append([toVariable(i,j,N)+3])
    elif map[i][j]['presence'] == "Croco":
        listClause.append([toVariable(i,j,N)+2])
    if (map[i][j]['voisinsTigre'] is not None and map[i][j]['voisinsCroco'] is not None and map[i][j]['voisinsRequin'] is not None) and (map[i][j]['voisinsTigre'] > 0 or map[i][j]['voisinsCroco'] > 0 or map[i][j]['voisinsRequin'] >0):
        listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsTigre'],2,N)
        listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsCroco'],1,N)
        listClause+= clauseNbVoisins(getVoisin(i,j,N,M),map[i][j]['voisinsRequin'],0,N)
    return listClause

"""
 mets a jour les clauses et regenere le dimacs
"""   
def updateMap(infos,map, toVisit,caseRestante,clauses,N,M):
    for info in infos:
        i = info["pos"][0]
        j = info["pos"][1]
        map[i][j]["terrain"] = info["field"]
        if "prox_count" in info.keys():
            if(not map[i][j]["visited"]):
                caseRestante-=1
            map[i][j]["visited"] = True
            map[i][j]["presence"] = "Nothing"
            map[i][j]["voisinsTigre"] = info["prox_count"][0]
            map[i][j]["voisinsRequin"] = info["prox_count"][1]
            map[i][j]["voisinsCroco"] = info["prox_count"][2]
        elif map[i][j]["visited"]==False:
            toVisit.append([i,j])
        clauses+= encodeCell(i,j,N,M,map)
    write_dimacs_file(gen(clauses,N,M),"test.cnf")
    return map,caseRestante

"""
genere les clauses : k animaux sur la map
deprecated car trop de clauses
"""

def clauseTotalEnnemi(nb : int,type : int, M: int, N:int):
    listClause = []
    listCase=[]
    for i in  range(M) :
        for j in range(N) :
            listCase.append(toVariable(i,j,N))
    listCombinations = list(combinations(listCase,nb))
    for c in listCombinations:
        clause = []
        for elem in c:
            clause.append(-(elem+type + 2))
        for var in listCase:
            if var not in c:
                copy = clause.copy()
                copy.append(-(var+type + 2))
                listClause.append(copy)
    listCombinations = list(combinations(listCase,N*M-nb))
    for c in listCombinations:
        clause = []
        for elem in c:
            clause.append(elem+type+2)
        for var in listCase:
            if var not in c:
                copy = clause.copy()
                copy.append(var+type+2)
                listClause.append(copy)
    return listClause
"""
genere les clauses k animaux dans les cases non decouvertes
"""
def clauseRestante(N,M,currentMap,caseRestante,requinRestant,crocoRestant,tigreRestant):
    return clauseNbVoisins(getLastCell(currentMap,N,M),requinRestant,0,N)+clauseNbVoisins(getLastCell(currentMap,N,M),crocoRestant,1,N)+clauseNbVoisins(getLastCell(currentMap,N,M),tigreRestant,2,N)
"""
appelle les fonction de generation de clause
"""
def genereAllclause(N,M,currentMap):
    return clauseUniqueRequinCroco(N,M)+clauseUniqueTigreCroco(N,M)+clauseUniqueTigreRequin(N,M)+encodeMap(currentMap)
"""
genere le string qui devra etre ecrit dans le dimacs
"""
def gen(clauses,N,M):
    #print(clauses)
    strg = "p cnf "+str(N*M*3)+" "+str(len(clauses)+1)+"\n"
    for i in clauses:
        for j in i:
            strg+=str(j)+" "
        strg+="0\n"
    return strg

"""
check si il y a un requin (si cela est possible : le sol est pas de la terre et possibilité requin)
ajoute la clause pas de requin -> si unsat alors il y a un requin
"""

def checkRequin(i, j, N, M, map,requinRestant):
    if(map[i][j]['terrain'] != 'land' and requinRestant > 0 and checkRequinUseful(i,j,map,N,M)):
        clause = str(-toVariable(i, j, N)-1)+" 0"
        if testDimacs(clause):
            return True
        else:
            return False
    return False

def checkTigre(i, j, N, M, map, tigreRestant):
    if(map[i][j]['terrain'] != 'sea' and tigreRestant > 0 and checkTigreUseful(i,j,map,N,M)):
        clause = str(-toVariable(i, j, N)-3)+" 0"
        if testDimacs(clause):
            return True
        else:
            return False
    return False

def checkCroco(i, j, N, M, map, crocoRestant):
    if(crocoRestant > 0 and checkCrocoUseful(i,j,map,N,M)):
        clause = str(-toVariable(i, j, N)-2)+" 0"
        if testDimacs(clause):
            return True
        else:
            return False
    return False


"""
check si la case est safe 
ajoute la clause requin ou croco ou tigre -> si unsat alors il y a un requin
"""


def checkSafe(i, j, N,):
    clause = str(toVariable(i, j, N)+1)+" "+str(toVariable(i, j, N)+2)+" "+str(toVariable(i, j, N)+3)+" 0"
    if testDimacs(clause):
        return True
    else:
        return False

"""
non utilisée
"""
def checkNoSafe(i, j, N, M,clauses):

    clauseSafe=[toVariable(i, j, N)-1,toVariable(i, j, N)-2,toVariable(i, j, N)-3]
    clauses.append(clauseSafe)
    write_dimacs_file(gen(clauses,N,M),"test.cnf")
    clauses.pop()
    if exec_gophersat("test.cnf","gophersat-1.1.6.exe")==False:
        return True
    else:
        return False

"""
non utilisée
"""
def nbAnimalInToVisit(toVisit,clauses,N,M,currentMap):
    write_dimacs_file(gen(clauses,N,M),"remaining.cnf")
    bool,res = exec_gophersat("remaining.cnf","gophersat-1.1.6.exe")
    S = 0
    T = 0
    C = 0
    for v in toVisit:
        toTest = False
        for voisin in getVoisin(v[0],v[1],N,M):
            if currentMap[voisin[0]][voisin[1]]["voisinsTigre"] != None:
                toTest = True
                break
        if toTest:
            if res[toVariable(v[0],v[1],N)+1] > 0:
                C+=1
            elif res[toVariable(v[0],v[1],N)+2] > 0:
                T+=1
            elif res[toVariable(v[0],v[1],N)+3] > 0:
                S+=1
    return S,C,T

"""
avant de tester l'aleatoire : essaye de check une case inconnue (cas tres rare)
"""

def pseudoAleatoire( N, M, caseRestante, clauses, currentMap, toVisit, croco):
    i = 0
    j = 0
    while i<M and currentMap[i][j]["terrain"]!=None:
        j+=1
        if j == N:
            j = 0
            i += 1
    if i >= M:
        return False
    if(checkSafe(i, j, N)):
        status, msg, infos = croco.discover(i, j)
        currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
        return True
    return False


"""
test aleatoire : calcul proba pour chaque case dans tt visit et une proba approximative pour l'ensemble des cases non visité 
et discover la case la plus faible
"""
def aleatoire(toVisit,clauses,N,M,currentMap, caseRestante, requinRestant,tigreRestant, crocoRestant):
    min = 10
    elem = None
    for v in toVisit:
        val = getGetProbaCase(v[0],v[1],currentMap,N,M)
        if(val !=0 and val < min):
            elem = v
            min = val
    if( caseRestante!=len(toVisit) and (requinRestant+tigreRestant+crocoRestant)/caseRestante<=min):
        i = 0
        j = 0
        while i<M and currentMap[i][j]["terrain"]!=None:
            j+=1
            if j == N:
                j = 0
                i += 1
        if i >= M:
            
        # crash detecté lors du final elem peut etre None
            return elem
        return [i,j]
    else:
        return elem
