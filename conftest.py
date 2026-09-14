import pytest

from server import app, loadClubs, loadCompetitions
import server


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_data():
    """Recharge les données de clubs et compétitions depuis les fichiers
    JSON avant chaque test, pour éviter les effets de bord entre tests
    (purchasePlaces modifie ces objets en mémoire)."""
    server.clubs = loadClubs()
    server.competitions = loadCompetitions()
    yield