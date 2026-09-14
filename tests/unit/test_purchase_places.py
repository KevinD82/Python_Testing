"""Tests unitaires - réservation de places. Branche bug/purchase-places-limits."""


def get_competition(name):
    from server import competitions
    return next(c for c in competitions if c['name'] == name)


def get_club(name):
    from server import clubs
    return next(c for c in clubs if c['name'] == name)


def test_valid_booking_deducts_points_and_places(client):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '5'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"complete" in response.data.lower() or b"confirm" in response.data.lower()

    competition = get_competition('Spring Festival')
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 20
    assert int(club['points']) == 8


def test_cannot_book_more_places_than_available(client):
    """On force un stock de places réduit pour déclencher précisément
    la règle des places disponibles (et non celle des 12 places max).

    Note : l'ancienne version de ce test demandait 20 places, ce qui
    déclenchait en réalité la règle des 12 places max plutôt que celle
    des places disponibles. Le test passait quand même par coïncidence,
    car le mot "available" apparaît dans un texte statique de
    welcome.html, pas dans le message d'erreur réellement testé.
    """
    competition = get_competition('Spring Festival')
    competition['numberOfPlaces'] = 5  # simulation d'un stock faible

    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '8'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "disponibles".encode('utf-8') in response.data.lower()

    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 5
    assert int(club['points']) == 13


def test_cannot_book_more_than_twelve_places(client):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '13'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"12" in response.data

    competition = get_competition('Spring Festival')
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 25
    assert int(club['points']) == 13


def test_cannot_book_more_places_than_club_points(client):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Iron Temple', 'places': '5'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"point" in response.data.lower()

    competition = get_competition('Spring Festival')
    club = get_club('Iron Temple')
    assert int(competition['numberOfPlaces']) == 25
    assert int(club['points']) == 4


def test_booking_exact_available_places_succeeds(client):
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Fall Classic', 'club': 'She Lifts', 'places': '12'},
        follow_redirects=True,
    )
    assert response.status_code == 200

    competition = get_competition('Fall Classic')
    club = get_club('She Lifts')
    assert int(competition['numberOfPlaces']) == 1
    assert int(club['points']) == 0


def test_purchase_with_unknown_club_or_competition_does_not_crash(client):
    """Couvre le garde-fou club/compétition inconnu de purchasePlaces
    (lignes non testées jusqu'ici)."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Competition Inconnue', 'club': 'Simply Lift', 'places': '1'},
    )
    assert response.status_code == 302
    assert response.location == '/'