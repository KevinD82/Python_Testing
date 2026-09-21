# Rapport de performance — Projet GUDLFT

## 1. Objectif

Les spécifications fonctionnelles (phase 2) imposent deux exigences de performance, justifiées par le nombre potentiellement élevé d'utilisateurs simultanés sur la plateforme :

- **Récupération de la liste des compétitions** : moins de 5 secondes.
- **Mise à jour du total de points** (réservation) : moins de 2 secondes.

Le guide de développement précise un nombre d'utilisateurs par défaut de **6** pour ces tests.

## 2. Outil et méthodologie

Les tests de charge ont été réalisés avec **Locust 2.46.5**, sur le serveur de développement Flask exécuté en local (`http://127.0.0.1:5000`).

### Scénarios simulés (`locustfile.py`)

| Scénario | Route testée | Poids relatif | Exigence associée |
|---|---|---|---|
| Connexion et consultation des compétitions | `POST /showSummary` | 3 | < 5 secondes |
| Réservation de places | `POST /purchasePlaces` | 1 | < 2 secondes |
| Consultation du tableau des points | `GET /points` | 1 | — |

Chaque requête est vérifiée automatiquement dans le code du scénario : si le temps de réponse dépasse le seuil correspondant, la requête est marquée en échec (`response.failure(...)`).

### Configuration du test

- **Nombre d'utilisateurs simultanés** : 6 (valeur par défaut du guide)
- **Ramp-up** : 6 utilisateurs démarrés immédiatement
- **Durée d'observation** : environ 30 à 60 secondes

## 3. Résultats obtenus

| Route | # Requêtes | # Échecs | Médiane (ms) | 95e percentile (ms) | Moyenne (ms) | Max (ms) |
|---|---|---|---|---|---|---|
| `GET /points` | 7 | 0 | 4 | 8 | 4,75 | 8 |
| `POST /purchasePlaces` | 13 | 0 | 4 | 58 | 13,7 | 58 |
| `POST /showSummary` | 34 | 0 | 6 | 58 | 12,55 | 58 |
| **Total agrégé** | **54** | **0** | **5** | **58** | **11,81** | **58** |

## 4. Analyse par rapport aux exigences

| Exigence | Seuil | Résultat mesuré | Marge |
|---|---|---|---|
| Liste des compétitions (`/showSummary`) | < 5 000 ms | 58 ms (maximum observé) | ~86 fois plus rapide que le seuil |
| Mise à jour des points (`/purchasePlaces`) | < 2 000 ms | 58 ms (maximum observé) | ~34 fois plus rapide que le seuil |

**Aucun échec** n'a été enregistré sur les 54 requêtes envoyées (`# Fails` = 0, `Failures/s` = 0) : les deux exigences de performance sont largement respectées, avec une marge très confortable.

## 5. Interprétation

Ces temps de réponse très courts s'expliquent par l'architecture actuelle du prototype : les données (clubs et compétitions) sont chargées une fois en mémoire au démarrage du serveur, à partir de fichiers JSON, sans appel à une base de données externe ni traitement lourd. Cela minimise la latence de chaque requête, conformément à l'esprit du guide de développement (« veillez à aller le plus vite possible »).

## 6. Limites du test réalisé

- Le test a été exécuté sur le **serveur de développement Flask** (mono-thread par défaut), non représentatif d'un déploiement en production avec un serveur WSGI dédié (Gunicorn, uWSGI...).
- Le volume de données (3 clubs, 2 compétitions) reste celui du prototype ; un volume de données réel plus important pourrait avoir un impact sur les temps de réponse, notamment sur les recherches linéaires (`next(...)`) dans les listes de clubs et compétitions.
- Le test a été mené en local, sans latence réseau réelle entre client et serveur.

## 7. Conclusion

Sur la configuration testée (6 utilisateurs simultanés, données du prototype), les deux exigences de performance des spécifications fonctionnelles sont respectées avec une marge très large. Aucune optimisation supplémentaire n'est nécessaire à ce stade du projet.

*(Voir capture d'écran jointe de l'interface Locust présentant ces résultats.)*
