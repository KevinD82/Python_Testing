"""Tests d'intégration - sauvegarde des données dans les fichiers JSON."""

import json

import server


def read_json(path, key):
    with open(path, encoding='utf-8') as f:
        return json.load(f)[key]


def test_booking_is_written_to_json_files(client):
    # Une réservation valide de 5 places pour Simply Lift (13 points) sur Spring Festival (25 places)
    client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '5'},
    )

    # On relit les fichiers (les copies temporaires du test), pas la mémoire du serveur
    clubs = read_json(server.CLUBS_FILE, 'clubs')
    competitions = read_json(server.COMPETITIONS_FILE, 'competitions')
    club = next(c for c in clubs if c['name'] == 'Simply Lift')
    competition = next(c for c in competitions if c['name'] == 'Spring Festival')

    assert int(club['points']) == 8
    assert int(competition['numberOfPlaces']) == 20