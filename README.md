# GUDLFT Registration

## Présentation

GUDLFT Registration est une application web développée avec Flask permettant aux secrétaires de clubs de réserver des places pour des compétitions sportives.

Cette application constitue un prototype simplifié du système de réservation utilisé par GUDLFT pour la gestion des compétitions régionales.

L'application permet :

- La connexion des secrétaires de club via leur adresse e-mail.
- La consultation des compétitions disponibles.
- La réservation de places pour une compétition.
- La consultation des points des clubs.
- La déconnexion de l'application.

Les données sont actuellement stockées dans des fichiers JSON afin d'éviter l'utilisation d'une base de données durant cette phase du projet.

---

## Technologies utilisées

- Python 3.14
- Flask
- Pytest
- Coverage
- Ruff

---

## Installation

### Cloner le dépôt

```bash
git clone <url-du-repo>
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

Les adresses suivantes peuvent être utilisées pour se connecter :

| Club | Email |
|--------|--------|
| Simply Lift | john@simplylift.co |
| Iron Temple | admin@irontemple.com |
| She Lifts | kate@shelifts.co.uk |

---

## Structure du projet

```text
Python_Testing/
│
├── templates/
│   ├── index.html
│   ├── welcome.html
│   └── booking.html
│
├── tests/
│   └── test_server.py
│
├── clubs.json
├── competitions.json
├── server.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Données de l'application

### clubs.json

Contient :

- le nom du club ;
- son adresse e-mail ;
- son nombre de points.

### competitions.json

Contient :

- le nom de la compétition ;
- la date ;
- le nombre de places disponibles.

---

## Exécution des tests

Lancer l'ensemble des tests :

```bash
pytest
```

Mode détaillé :

```bash
pytest -v
```

---

## Couverture de tests

Générer la couverture :

```bash
coverage run -m pytest
```

Afficher le rapport :

```bash
coverage report
```

Générer un rapport HTML :

```bash
coverage html
```

Le rapport sera disponible dans :

```text
htmlcov/index.html
```

---

## Qualité du code

Vérification avec Ruff :

```bash
ruff check .
```

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