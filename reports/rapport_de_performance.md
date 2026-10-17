# Rapport de performance — Projet GUDLFT

## 1. Objectif

Les spécifications fonctionnelles fixent deux exigences :

- Liste des compétitions : moins de **5 secondes**.
- Mise à jour des points (réservation) : moins de **2 secondes**.

Le nombre d'utilisateurs simultanés retenu est **6** (valeur du guide de développement).

## 2. Méthode

- Outil : **Locust 2.46.5**, sur le serveur Flask local (`http://127.0.0.1:5000`).
- Données remises à zéro avant le test (`git restore clubs.json competitions.json`), serveur démarré après la restauration.
- Durée : environ 15 secondes, 6 utilisateurs.

| Scénario | Route | Poids | Seuil |
|---|---|---|---|
| Connexion et liste des compétitions | `POST /showSummary` | 3 | < 5 s |
| Réservation de places | `POST /purchasePlaces` | 1 | < 2 s |
| Tableau des points | `GET /points` | 1 | — |

Une requête est marquée en **échec** si le seuil est dépassé. Une réservation **refusée** est aussi un échec : elle n'est plus comptée comme un succès.

## 3. Résultats

| Route | Requêtes | Échecs | Moyenne (ms) | Médiane (ms) | 95e percentile (ms) | Max (ms) |
|---|---|---|---|---|---|---|
| `GET /points` | 8 | 0 | 7 | 6 | 10 | 10 |
| `POST /purchasePlaces` | 10 | 0 | 9 | 5 | 19 | 18 |
| `POST /showSummary` | 27 | 0 | 6 | 6 | 12 | 25 |
| **Total** | **45** | **0** | **7** | **6** | **16** | **25** |

## 4. Analyse

| Exigence | Seuil | Maximum mesuré |
|---|---|---|
| Liste des compétitions | < 5 000 ms | 25 ms |
| Mise à jour des points | < 2 000 ms | 18 ms |

**0 échec sur 45 requêtes** : les deux exigences sont respectées avec une très large marge. Les 10 réservations ont toutes été acceptées, donc le test ne dégrade pas le stock de places.

## 5. Limites

- Serveur de développement Flask, non représentatif d'une production (Gunicorn, etc.).
- Petit volume de données (3 clubs, 3 compétitions) et test en local, sans latence réseau.
- Le stock de places et de points est limité : le test est volontairement court. Une fois le stock épuisé, les réservations sont refusées par conception et comptées en échec.
- Avant un nouveau test : restaurer les JSON, puis redémarrer le serveur.

## 6. Conclusion

Avec 6 utilisateurs simultanés, les exigences de performance sont respectées. Aucune optimisation n'est nécessaire à ce stade.

*(Voir la capture d'écran de l'interface Locust dans `reports/`.)*