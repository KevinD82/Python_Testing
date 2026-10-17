import shutil

import pytest

import server
from server import app, loadClubs, loadCompetitions


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_data(tmp_path, monkeypatch):
    """Chaque test travaille sur une copie jetable des fichiers JSON.

    tmp_path est un dossier temporaire propre à chaque test. monkeypatch
    pointe le serveur vers ces copies et remet tout en place après le test :
    les vrais fichiers ne sont jamais touchés.
    """
    for name in ('clubs.json', 'competitions.json'):
        shutil.copy(name, tmp_path / name)
    monkeypatch.setattr(server, 'CLUBS_FILE', str(tmp_path / 'clubs.json'))
    monkeypatch.setattr(server, 'COMPETITIONS_FILE', str(tmp_path / 'competitions.json'))

    server.clubs = loadClubs()
    server.competitions = loadCompetitions()
    server.bookings = {}
    yield