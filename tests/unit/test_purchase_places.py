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
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Fall Classic', 'club': 'She Lifts', 'places': '20'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"disponible" in response.data.lower() or b"available" in response.data.lower()

    competition = get_competition('Fall Classic')
    club = get_club('She Lifts')
    assert int(competition['numberOfPlaces']) == 13
    assert int(club['points']) == 12


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