import pytest

import server
from server import app, loadClubs, loadCompetitions


@pytest.fixture
def client():
    """Fixture Pytest pour initialiser un client de test HTTP Flask.

    Cette fixture permet de simuler des requêtes HTTP (GET, POST)
    sur l'application sans lancer le serveur de développement web.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_data():
    """Recharge les données de clubs et compétitions depuis les fichiers
    JSON avant CHAQUE test.

    Nécessaire car purchasePlaces modifie les objets clubs/competitions
    directement en mémoire (numberOfPlaces, points). Sans cette remise
    à zéro, un test de réservation fausserait les tests suivants
    (dépendance à l'ordre d'exécution).
    """
    server.clubs = loadClubs()
    server.competitions = loadCompetitions()
    yield