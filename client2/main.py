"""
[IA02] Projet généralisation mastermind
author:  Ollivier Emma, Guichard Amaury
version: 1.0.0
"""
from clauses import *
from fun import *
from typing import *
from itertools import *
from crocomine_client import CrocomineClient
import time

server = "http://croco.lagrue.ninja:80"
group = "Groupe 12"
members = "Emma Ollivier et Amaury Guichard"
croco = CrocomineClient(server, group, members,"dangoreven")




def play(nb):

    start_time = time.time()
    status, msg, grid_infos = croco.new_grid()
    
    if status == "Err":
        return
    N=grid_infos["n"]
    M=grid_infos["m"]
    caseRestante = N*M
    status, msg, infos = croco.discover(grid_infos["start"][0],grid_infos["start"][1])
    currentMap = createMapFromInfo(grid_infos)
    toVisit=[]   
    requinRestant=grid_infos["shark_count"]
    tigreRestant=grid_infos["tiger_count"]
    crocoRestant=grid_infos["croco_count"]
    
    clauses = genereAllclause(N,M,currentMap)
    write_dimacs_file(gen(clauses,N,M),"test.cnf")
    currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
    


    nbCoups = 0
    edited = False
    stuck = False
    reallyStuck = False
    lastElem = None
    lastEdited=[]
    wasStuck = False

    
    while(toVisit and status=="OK"):

        """
        Si un animal a été decouvert ou verifie et chord les cases autour

        """
        if edited:
            tabVoisin=getVoisin(lastEdited[0], lastEdited[1], N, M)
            for i in range(len(tabVoisin)):
                if(checkChord(currentMap,N,M,tabVoisin[i][0],tabVoisin[i][1])):
                    status, msg, infos = croco.chord(tabVoisin[i][0],tabVoisin[i][1])
                    currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
                    nbCoups+=1
            edited = False

        """
        Si bloqué on ajoute les clauses 'il reste k animaux a decouvrir' en plus (si cela ne genere pas trop de clause)
        """   
        if stuck:
            c = clauseRestante(N,M,currentMap,caseRestante,requinRestant,crocoRestant,tigreRestant)
            if(len(c)<100000):
                clauses += c
            stuck=False
            wasStuck = True
            
        """
        on va tester elem
        parfois elem est deja visité, on le retir
        """
        elem = toVisit.pop(0)
        while currentMap[elem[0]][elem[1]]["visited"]:
            elem = toVisit.pop(0)
        found = False



        
        """
        verifie si case safe puis si requin, tigre ou croco et maj les clauses et la map en consequence
        """
        if(checkSafe(elem[0], elem[1], N)):
            found = True
            currentMap[elem[0]][elem[1]]["visited"] = True
            caseRestante -= 1
            status, msg, infos = croco.discover(elem[0], elem[1])
            currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
            nbCoups+=1
            #edited = True
            lastElem=None
            stuck=False
            reallyStuck=False

        
       

        elif(checkRequin(elem[0], elem[1], N, M, currentMap, requinRestant)):
    
            found = True
            #print("Requin ",elem[0], elem[1])   
            status, msg, infos = croco.guess(elem[0], elem[1], 'S')
            currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
            currentMap[elem[0]][elem[1]]["visited"] = True
            currentMap[elem[0]][elem[1]]["presence"] = 'Requin'
            requinRestant -= 1
            caseRestante -= 1
            nbCoups+=1
            edited = True
            lastElem=None
            stuck=False
            reallyStuck=False
            lastEdited=elem
            """
            On remonte les voisins pour les tester en priorité : plus de chance deduire qqch
            """
            for v in getVoisin(elem[0], elem[1], N, M):
                if v in toVisit:
                    toVisit.remove(v)
                    toVisit.insert(0,v)


        elif(checkCroco(elem[0], elem[1], N, M, currentMap,crocoRestant)):

            found = True
            #print("Croco ",elem[0], elem[1])   
            status, msg, infos = croco.guess(elem[0], elem[1], 'C')
            currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
            currentMap[elem[0]][elem[1]]["visited"] = True
            currentMap[elem[0]][elem[1]]["presence"] = 'Croco'
            crocoRestant -= 1
            caseRestante -= 1
            nbCoups+=1
            edited = True
            lastElem=None
            stuck=False
            reallyStuck=False
            lastEdited=elem
            for v in getVoisin(elem[0], elem[1], N, M):
                if v in toVisit:
                    toVisit.remove(v)
                    toVisit.insert(0,v)


        elif(checkTigre(elem[0], elem[1], N, M, currentMap, tigreRestant)):
            found = True
            #print("Tigre ",elem[0], elem[1])   
            status, msg, infos = croco.guess(elem[0], elem[1], 'T')
            currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
            currentMap[elem[0]][elem[1]]["visited"] = True
            currentMap[elem[0]][elem[1]]["presence"] = 'Tigre'
            tigreRestant -= 1
            caseRestante -= 1
            nbCoups+=1
            edited = True
            lastElem=None
            stuck=False
            reallyStuck=False
            lastEdited=elem
            for v in getVoisin(elem[0], elem[1], N, M):
                if v in toVisit:
                    toVisit.remove(v)
                    toVisit.insert(0,v)

        """
        si rien de deduit on sauvegarde, si on rerencontre plus tard la case sans modif alors on est coincé
        on ajoute les clauses restantes si tjs bloqué pseudo aleatoire si tjs bloqué aleatoire
        """
        if(not found):

            toVisit.append(elem)

            if(wasStuck==True):
 
                if(elem == lastElem):
                    reallyStuck=True
                    if pseudoAleatoire(N, M, caseRestante,clauses, currentMap, toVisit, croco):
                        nbCoups+=1
                        reallyStuck=False
                    else :
                        [i,j] = aleatoire(toVisit,clauses,N,M,currentMap,caseRestante, requinRestant,tigreRestant, crocoRestant)
                        currentMap[i][j]["visited"]=True
                        status, msg, infos = croco.discover(i,j)
                        currentMap,caseRestante = updateMap(infos,currentMap, toVisit,caseRestante,clauses,N,M)
                        nbCoups+=1
                        stuck = False
            if(elem == lastElem):
                stuck=True
            if lastElem == None:
                lastElem = elem
                    



        

    if(status!="KO"):
        nb+=1
        print(nb," maps reussie")
    else:
        print("Echec")

    print("Fini %d --- %s seconds ---" % (nbCoups,time.time() - start_time))
    play(nb)
      



play(0)
