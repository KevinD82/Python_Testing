# Rapport de tests — Projet GUDLFT

## 1. Méthode

Chaque correction ou fonctionnalité suit le même cycle :

1. Écriture du test (RED : il échoue et confirme le problème).
2. Correction du code.
3. Le test passe (GREEN).
4. Une branche Git par sujet, avec un commit pour la correction et un commit pour les tests.

Les cas nominaux (happy paths) et les cas d'erreur (sad paths) sont testés.

## 2. Organisation des tests

Les tests sont séparés en deux familles :

| Famille | Dossier | Rôle | Tests |
|---|---|---|---|
| Unitaires | `tests/unit/` | Testent la logique métier seule (`booking_rules.py`), sans Flask ni fichiers | 17 |
| Intégration | `tests/integration/` | Testent les routes Flask avec le client de test | 29 |

Les tests d'intégration travaillent sur des **copies temporaires** des fichiers JSON (fixture dans `tests/integration/conftest.py`) : les vrais fichiers ne sont jamais modifiés et les tests restent indépendants les uns des autres.

## 3. Ce qui est testé

| Sujet | Vérifié par |
|---|---|
| Connexion : e-mail inconnu, vide ou absent, sans crash | `test_login.py` |
| Page de réservation : club ou compétition inconnu, compétition passée refusée | `test_book_route.py` |
| Page de réservation : saisie limitée (`min`, `max`), formulaire masqué si rien n'est réservable | `test_book_route.py` |
| Réservation : places disponibles, points du club, déduction des places et des points | `test_purchase_places.py` |
| Réservation : maximum de 12 places, y compris en plusieurs réservations | `test_purchase_places.py` |
| Réservation : 0, négatif, vide ou non numérique refusés | `test_purchase_places.py` |
| Compétition passée : visible mais non réservable | `test_login.py`, `test_purchase_places.py` |
| Enregistrement des réservations dans les fichiers JSON | `test_persistence.py` |
| Tableau public des points (lecture seule, sans connexion) | `test_points_board.py` |
| Déconnexion | `test_logout.py` |
| Règles de réservation seules, sans Flask | `tests/unit/test_booking_rules.py` |

## 4. Résultat

```
46 passed
```

`ruff check .` : aucune erreur.

## 5. Couverture de code

Commande : `coverage run --omit="tests/*" -m pytest`

| Fichier | Instructions | Non couvertes | Couverture |
|---|---|---|---|
| `booking_rules.py` | 15 | 0 | 100 % |
| `server.py` | 83 | 0 | 100 % |
| **Total** | **98** | **0** | **100 %** |

L'objectif minimum était de 60 %. Le rapport mesure uniquement le code de l'application (les fichiers de tests sont exclus).

*(Voir la capture d'écran du rapport HTML dans `reports/`.)*

### Point de vigilance

Une couverture de 100 % prouve que chaque ligne a été exécutée, pas que les tests sont pertinents. Un test était passé « par coïncidence » : le mot cherché apparaissait dans le texte fixe de la page et non dans le message d'erreur. Les tests vérifient maintenant des messages précis (par exemple « disponibles », « 12 places », « terminée »).

## 6. Organisation Git

Une branche par sujet (correction, fonctionnalité, tests), fusionnée dans `master` par Pull Request puis conservée. La branche `QA` contient le travail commenté et n'est jamais fusionnée dans `master`.