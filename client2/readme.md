# Lancement 

	python main.py
	
# Spécificité 

- Utilisation de chords sur les voisins lors de guess
- Pas de reecriture du dimacs pour les guess (edition du fichier plutot que reecriture)
- Trie des cases à visiter : si on obtient des infos sur une case à visiter, on la visite en priorité
- Avant de faire un appel dimacs pour guess : verification du type de terrain, du nombre d'animaux restants et si tous les voisins ont dans leur voisinages un animal non decouvert
- Si bloqué -> utilisation des clauses `il reste k animal à decouvrir` -> si encore bloqué, test dimacs sur une case sans infos -> si encore bloqué, aléatoire
- Aléatoire : calcul probabilité de presence sur chaque case à visiter et sur les cases non decouvertes : discover sur la case avec la probabilité la plus basse
- Pas de régénération des clauses, uniquement ajout dans le tableau de clauses
