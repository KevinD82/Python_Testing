# GUDLFT Registration
 
## Présentation
 
GUDLFT Registration est une application web développée avec Flask permettant aux secrétaires de clubs de réserver des places pour des compétitions sportives.
 
Cette application constitue un prototype simplifié du système de réservation utilisé par GUDLFT pour la gestion des compétitions régionales.
 
L'application permet :
 
- La connexion des secrétaires de club via leur adresse e-mail.
- La consultation des compétitions (les compétitions passées restent visibles mais ne sont plus réservables).
- La réservation de places pour une compétition, dans le respect des règles métier ci-dessous.
- La consultation publique des points de tous les clubs.
- La déconnexion de l'application.
Les données sont stockées dans des fichiers JSON (pas de base de données à ce stade). Chaque réservation valide est enregistrée dans ces fichiers.
 
---
 
## Technologies utilisées
 
- Python 3.14 (version utilisée pour le développement et les tests)
- Flask
- Pytest
- Coverage
- Ruff
- Locust (tests de performance)
---
 
## Installation
 
### Cloner le dépôt
 
```bash
git clone https://github.com/KevinD82/Python_Testing.git
cd Python_Testing
```
 
### Créer un environnement virtuel
 
```bash
python -m venv venv
```
 
### Activer l'environnement virtuel
 
#### Windows PowerShell
 
```powershell
.\venv\Scripts\Activate.ps1
```
 
#### Linux / macOS
 
```bash
source venv/bin/activate
```
 
Lorsque l'environnement est activé, l'invite de commande doit afficher :
 
```text
(venv)
```
 
### Installer les dépendances
 
```bash
pip install -r requirements.txt
```
 
---
 
## Lancement de l'application
 
### Windows PowerShell
 
```powershell
$env:FLASK_APP="server.py"
```
 
### Linux / macOS
 
```bash
export FLASK_APP=server.py
```
 
Puis démarrer le serveur :
 
```bash
flask run
```
 
ou
 
```bash
python -m flask run
```
 
L'application sera accessible à l'adresse :
 
```text
http://127.0.0.1:5000
```
 
---
 
## Comptes de test
 
| Club | Email | Points |
|--------|--------|--------|
| Simply Lift | john@simplylift.co | 13 |
| Iron Temple | admin@irontemple.com | 4 |
| She Lifts | kate@shelifts.co.uk | 12 |
 
Compétitions fournies : Spring Festival et Fall Classic (dates futures, réservables) et Winter Open (date passée, non réservable).
 
---
 
## Règles de réservation
 
Elles sont centralisées dans `booking_rules.py` (code pur, sans Flask, testable seul). Une réservation est refusée, avec un message explicite, dans cet ordre :
 
1. La compétition est terminée.
2. Le nombre de places demandé n'est pas un entier positif (0, négatif, vide ou non numérique).
3. Le club dépasserait 12 places au total pour cette compétition (cumul de plusieurs réservations).
4. Le nombre de places demandé dépasse les places disponibles.
5. Le nombre de places demandé dépasse les points du club (1 point = 1 place).
Une réservation valide déduit les places de la compétition et les points du club, puis écrit les deux fichiers JSON.
 
Côté interface, la page de réservation limite la saisie (`min="1"`, `max` = maximum réservable) et masque le formulaire quand le club ne peut rien réserver : l'utilisateur est informé avant de valider.
 
---
 
## Routes
 
| Route | Méthode | Rôle |
|--------|--------|--------|
| `/` | GET | Page d'accueil (saisie de l'email) |
| `/showSummary` | POST | Connexion, affiche les compétitions |
| `/book/<competition>/<club>` | GET | Page de réservation |
| `/purchasePlaces` | POST | Validation et enregistrement d'une réservation |
| `/points` | GET | Tableau public des points des clubs |
| `/logout` | GET | Déconnexion |
 
---
 
## Structure du projet
 
```text
Python_Testing/
│
├── templates/
│   ├── index.html
│   ├── welcome.html
│   ├── booking.html
│   └── points.html
│
├── tests/
│   ├── unit/
│   │   └── test_booking_rules.py
│   └── integration/
│       ├── conftest.py
│       ├── test_book_route.py
│       ├── test_login.py
│       ├── test_logout.py
│       ├── test_persistence.py
│       ├── test_points_board.py
│       └── test_purchase_places.py
│
├── reports/
├── booking_rules.py
├── server.py
├── locustfile.py
├── clubs.json
├── competitions.json
├── pytest.ini
├── requirements.txt
├── README.md
└── .gitignore
```
 
---
 
## Données de l'application
 
### clubs.json
 
Contient le nom du club, son adresse e-mail et son nombre de points.
 
### competitions.json
 
Contient le nom de la compétition, la date (`AAAA-MM-JJ HH:MM:SS`) et le nombre de places disponibles.
 
### Persistance et remise à zéro
 
Chaque réservation valide met à jour `clubs.json` et `competitions.json`. Pour revenir aux données d'origine (avant une démonstration ou un test Locust) :
 
```bash
git restore clubs.json competitions.json
```
 
Puis **redémarrer le serveur** : il charge les fichiers au démarrage, sinon il garde l'ancien état en mémoire.
 
---
 
## Exécution des tests
 
```bash
pytest
```
 
Mode détaillé :
 
```bash
pytest -v
```
 
Les tests sont séparés en deux familles :
 
- `tests/unit/` : tests unitaires de la logique métier (`booking_rules.py`), sans Flask ni fichiers.
- `tests/integration/` : tests des routes Flask via le client de test. Ils travaillent sur des **copies temporaires** des fichiers JSON : les vrais fichiers ne sont jamais modifiés.
Pour lancer une famille seule :
 
```bash
pytest tests/unit
pytest tests/integration
```
 
---
 
## Couverture de tests
 
```bash
coverage run -m pytest
coverage report
coverage html
```
 
Le rapport HTML est disponible dans `htmlcov/index.html`.
 
---
 
## Tests de performance (Locust)
 
Le fichier `locustfile.py` simule des secrétaires de clubs qui consultent leur page, réservent des places et consultent le tableau des points. Une réservation refusée est comptée comme un **échec** (elle n'est plus comptée à tort comme un succès).
 
Procédure :
 
1. Remettre les données à zéro : `git restore clubs.json competitions.json`
2. Démarrer le serveur : `flask run`
3. Dans un second terminal : `locust -f locustfile.py --host http://127.0.0.1:5000`
4. Ouvrir `http://localhost:8089`, saisir par exemple 6 utilisateurs, une montée de 1 par seconde, et laisser tourner une quinzaine de secondes.
Le stock de places étant limité, le test est volontairement court : une fois les places ou les points épuisés, les réservations sont refusées par conception.
 
Les résultats sont détaillés dans `reports/rapport_de_performance.md`.
 
---
 
## Qualité du code
 
```bash
ruff check .
```
 
---
 
## Organisation du travail avec Git
 
- Une branche par correction ou fonctionnalité, avec des commits séparés pour le correctif et pour le test (`fix:`, `feat:`, `test:`, `refactor:`, `docs:`).
- Chaque branche est fusionnée dans `master` par Pull Request puis conservée.
- Une branche `QA` contient des commentaires explicatifs ; elle suit `master` mais n'y est jamais fusionnée.
---
 
## Limites connues
 
- Le cumul des 12 places par club et par compétition est conservé en mémoire : il est remis à zéro au redémarrage du serveur.
- Les données sont dans des fichiers JSON : adapté à un prototype, pas à une charge réelle (une base de données serait l'étape suivante).
---
 
## Objectifs du projet
 
- Corriger les anomalies présentes dans l'application.
- Ajouter les fonctionnalités demandées dans la phase 2.
- Atteindre un minimum de 60 % de couverture de code.
- Produire un rapport de tests.
- Produire un rapport de performances avec Locust.
- Respecter les bonnes pratiques Git et GitHub.
---
 
## Auteur
 
Projet réalisé dans le cadre de la formation Développeur d'Application Python OpenClassrooms.
 
Kevin Delcroix
 