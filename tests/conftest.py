import pytest

from server import app


@pytest.fixture
def client():
    """Fixture Pytest pour initialiser un client de test HTTP Flask.

    Cette fixture permet de simuler des requêtes HTTP (GET, POST)
    sur l'application sans lancer le serveur de développement web.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client