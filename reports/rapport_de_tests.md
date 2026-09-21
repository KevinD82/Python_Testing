# Rapport de tests — Projet GUDLFT

## 1. Contexte et méthodologie

Suite au rapport de QA v0.9.1 signalant plusieurs bogues (dont un crash critique de l'application), une démarche de Test-Driven Development (TDD) a été appliquée sur l'ensemble du prototype, conformément aux directives du guide de développement.

Pour chaque bogue ou fonctionnalité traité :
1. Écriture des tests en premier (phase RED — le test échoue et confirme le problème)
2. Correction du code ou implémentation de la fonctionnalité
3. Vérification que les tests passent (phase GREEN)
4. Une branche Git dédiée par sujet, avec un commit séparé pour la correction et pour les tests

Chaque fonctionnalité a été testée en couvrant à la fois les **happy paths** (cas nominaux) et les **sad paths** (cas d'erreur), conformément à la consigne du mail de Sam.

## 2. Bogues corrigés

### 2.1 Connexion (`showSummary`) — branche `fix/login-crash`

**Bogue** : un e-mail ne correspondant à aucun club provoquait un crash de l'application (`IndexError`, erreur 500) — c'est le bogue critique signalé dans le rapport de QA.

**Correction** : remplacement de la recherche par liste (`[0]`) par une recherche sécurisée (`next(..., None)`), avec redirection vers l'accueil et affichage d'un message d'erreur explicite si l'e-mail est introuvable.

**Tests (5)** :
| Test | Type | Résultat attendu |
|---|---|---|
| Chargement de la page d'accueil | Happy path | Code 200 |
| Connexion avec e-mail valide | Happy path | Affichage de la page de bienvenue avec les compétitions |
| E-mail inconnu | Sad path | Redirection (302) + message d'erreur, pas de crash |
| Champ e-mail manquant | Sad path | Pas de crash (code ≠ 500) |
| Champ e-mail vide | Sad path | Redirection (302), pas de crash |

### 2.2 Route de réservation (`book`) — branche `bug/book-route-crash`

**Bogue** : même schéma que le login — un club ou une compétition inconnu dans l'URL provoquait un crash.

**Correction** : même pattern de correction (`next(..., None)`), avec redirection et message d'erreur.

**Tests (4)** : page de réservation affichée si club/compétition valides, redirection propre si club inconnu, si compétition inconnue, message d'erreur affiché.

### 2.3 Réservation de places (`purchasePlaces`) — branche `bug/purchase-places-limits`

**Bogues et fonctionnalité manquante** :
- Aucune vérification du nombre de places disponibles (le compteur pouvait devenir négatif).
- Aucune limite des 12 places maximum par club et par compétition.
- Aucune vérification que le club possède assez de points.
- **Les points du club n'étaient jamais déduits** après une réservation (fonctionnalité de la phase 1 non implémentée).

**Correction** : ajout des trois vérifications métier, dans l'ordre (12 places → places disponibles → points suffisants), avec déduction conjointe des places et des points en cas de succès.

**Tests (6)** :
| Test | Type | Résultat attendu |
|---|---|---|
| Réservation valide | Happy path | Places et points déduits, message de confirmation |
| Réservation exacte du nombre de places restantes | Happy path (cas limite) | Succès, pas d'erreur off-by-one |
| Plus de places que disponibles | Sad path | Refus, aucune donnée modifiée |
| Plus de 12 places demandées | Sad path | Refus, aucune donnée modifiée |
| Points insuffisants | Sad path | Refus, aucune donnée modifiée |
| Club ou compétition inconnu | Sad path | Redirection, pas de crash |

### 2.4 Tableau public des points — branche `feature/points-board`

**Fonctionnalité manquante** (phase 2) : un tableau en lecture seule des points de tous les clubs, accessible sans connexion.

**Ajouts** : route `/points`, template `points.html`.

**Tests (3)** : accessibilité sans connexion, affichage correct des points de chaque club, absence de tout lien de réservation (garantie du caractère lecture seule).

### 2.5 Amélioration de la couverture — branche `test/coverage-improvements`

Ajout d'un test pour la déconnexion (`/logout`, jusque-là non couverte) et correction d'un test dont l'assertion ne validait pas le comportement réellement visé (voir section 4).

## 3. Résultat global des tests

```
19 passed in 0.15s
```

19 tests unitaires, répartis sur 5 fichiers de tests (`test_login.py`, `test_book_route.py`, `test_purchase_places.py`, `test_points_board.py`, `test_logout.py`), couvrant l'ensemble des routes de l'application avec leurs cas nominaux et leurs cas d'erreur.

## 4. Couverture de code

```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
conftest.py                             13      0   100%
server.py                               59      0   100%
tests\unit\test_book_route.py           16      0   100%
tests\unit\test_login.py                23      0   100%
tests\unit\test_logout.py                4      0   100%
tests\unit\test_points_board.py         16      0   100%
tests\unit\test_purchase_places.py      50      0   100%
--------------------------------------------------------
TOTAL                                  181      0   100%
```

**100% de couverture**, contre un objectif minimum de 60% fixé par le guide de développement.

*(Voir capture d'écran jointe du rapport HTML généré par `coverage html`.)*

### Point de vigilance méthodologique

Une couverture à 100% garantit que chaque ligne de code a été exécutée au moins une fois par les tests, mais **ne garantit pas à elle seule l'absence de bogue** : elle ne dit rien de la pertinence des assertions.

Exemple concret rencontré durant ce projet : le test `test_cannot_book_more_places_than_available` demandait initialement 20 places sur une compétition qui n'en avait que 13 disponibles. La ligne de code testée était bien exécutée, mais c'est en réalité la règle des **12 places maximum** qui se déclenchait en premier (20 > 12), et non celle des places disponibles. Le test passait malgré tout car le mot-clé recherché apparaissait par coïncidence dans un texte statique du template, sans rapport avec le message d'erreur réellement émis. Le test a été corrigé pour forcer un stock de places réduit et déclencher précisément le bon garde-fou.

## 5. Structure des tests

```
tests/
└── unit/
    ├── test_login.py
    ├── test_book_route.py
    ├── test_purchase_places.py
    ├── test_points_board.py
    └── test_logout.py
```

Une fixture `client` (client de test Flask) et une fixture `reset_data` (autouse, rechargeant les données JSON avant chaque test) sont définies dans `conftest.py`, afin d'isoler les tests les uns des autres — nécessaire car certaines routes modifient les données en mémoire.

## 6. Organisation Git

Une branche par correctif ou fonctionnalité, avec un commit dédié à la correction et un commit dédié aux tests :

| Branche | Contenu |
|---|---|
| `fix/login-crash` | Correction du crash de connexion + tests |
| `bug/book-route-crash` | Correction du crash de réservation + tests |
| `bug/purchase-places-limits` | Règles métier de réservation + tests |
| `feature/points-board` | Tableau public des points + tests |
| `test/coverage-improvements` | Comblement des trous de couverture |
| `test/locust-performance` | Tests de performance (voir rapport dédié) |
| `QA` | Branche d'assurance qualité regroupant l'ensemble du travail, non fusionnée dans `master` |
