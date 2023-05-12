# Projet_IA02

## Lancement 

	python main.py
	
## Spécificité 

- Utilisation de chords sur les voisins lors de guess
- Pas de reecriture du dimacs pour les guess (edition du fichier plutot que reecriture)
- Trie des cases à visiter : si on obtient des infos sur une case à visiter, on la visite en priorité
- Avant de faire un appel dimacs pour guess : verification du type de terrain, du nombre d'animaux restants et si tous les voisins ont dans leur voisinages un animal non decouvert
- Si bloqué -> utilisation des clauses `il reste k animal à decouvrir` -> si encore bloqué, test dimacs sur une case sans infos -> si encore bloqué, aléatoire
- Aléatoire : calcul probabilité de presence sur chaque case à visiter et sur les cases non decouvertes : discover sur la case avec la probabilité la plus basse


## Notation

Pour chaque case :
* possede requin
* possede croco
* possede tigre

= 3 vars par cellules

numérotation cases :

    0 | 1 | 2 | 3 | 4 
    5 | 6 | 7 | 8 | 9
    etc...

    passer de case a variable nbCase * 3 + ( 1 | 2 | 3 | 4 etc...)


## Dimacs

### clauses de bases

Au plus un animal par case : 3 clauses (élimination de doublons)

    possedeTigre -> non possedeRequin et non possedeCroco == ( non possedeTigre ou non possedeRequin ) et ( non possedeTigre ou non possedeCroco)
    possedeRequin -> non possedeTigre et non possedeCroco
    possedeCroco -> non possedeRequin et non possedetigre

Contraintes de terrains 

    Terre -> non possedeRequin
    Mer -> non possedeTigre
    // un seul sens utile ici car pas besoin deduire terrain mais sinon :
    possedeRequin -> Mer
    possedeTigre -> Terre

Contraintes sur la sur la quantité d'ennemis

...
    
### Clauses avancés ( arités )

Exemple : 3 voisins requins
 
	 V1R et V2R et V3R <-> non V4R et non V5R et non V6R et non V7R et non V8R

Beaucoup de clauses : itertools ?

## Stratégies

### Strat brutale

Encoder toutes infos qu'on a en dimacs

    pour chaque case 
        tester requin ou tigre ou croco
            si unsat alors case sure
            on appelle discover() et encode les nouvelles infos

### Strategie orientée

Meme que brutale mais selectionne les cases interessantes (voisins des cases decouvertes)

### Strategie avancé

Utilise des regles/stats pour accelerer 
