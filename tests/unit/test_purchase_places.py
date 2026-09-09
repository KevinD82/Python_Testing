"""
Tests unitaires pour la réservation de places (purchasePlaces) -
branche bug/purchase-places-limits.

Règles métier attendues (spécifications fonctionnelles, section "Le comment") :
1. Un club ne peut pas réserver plus de places qu'il n'en reste dans
   la compétition.
2. Un club ne peut pas réserver plus de 12 places pour une même
   compétition.
3. Un club ne peut pas utiliser plus de points qu'il n'en possède
   (1 point = 1 place).
4. Une réservation valide doit déduire les points ET les places, et
   confirmer le nombre de places achetées.

Données réelles utilisées (clubs.json / competitions.json) :
- Simply Lift  : 13 points
- Iron Temple  : 4 points
- She Lifts    : 12 points
- Spring Festival : 25 places
- Fall Classic    : 13 places
"""


def get_competition(name):
    from server import competitions
    return next(c for c in competitions if c['name'] == name)


def get_club(name):
    from server import clubs
    return next(c for c in clubs if c['name'] == name)


def test_valid_booking_deducts_points_and_places(client):
    """Happy path : réservation valide -> places ET points déduits,
    message de confirmation affiché."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '5'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"complete" in response.data.lower() or b"confirm" in response.data.lower()

    competition = get_competition('Spring Festival')
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 20  # 25 - 5
    assert int(club['points']) == 8  # 13 - 5


def test_cannot_book_more_places_than_available(client):
    """Sad path : impossible de réserver plus de places qu'il n'en
    reste dans la compétition. L'état ne doit pas changer."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Fall Classic', 'club': 'She Lifts', 'places': '20'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"disponible" in response.data.lower() or b"available" in response.data.lower()

    competition = get_competition('Fall Classic')
    club = get_club('She Lifts')
    assert int(competition['numberOfPlaces']) == 13  # inchangé
    assert int(club['points']) == 12  # inchangé


def test_cannot_book_more_than_twelve_places(client):
    """Sad path : impossible de réserver plus de 12 places, même si
    la compétition a assez de places et le club assez de points."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '13'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"12" in response.data

    competition = get_competition('Spring Festival')
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 25  # inchangé
    assert int(club['points']) == 13  # inchangé


def test_cannot_book_more_places_than_club_points(client):
    """Sad path : impossible d'utiliser plus de points que ce que
    le club possède (1 point = 1 place)."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Iron Temple', 'places': '5'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"point" in response.data.lower()

    competition = get_competition('Spring Festival')
    club = get_club('Iron Temple')
    assert int(competition['numberOfPlaces']) == 25  # inchangé
    assert int(club['points']) == 4  # inchangé


def test_booking_exact_available_places_succeeds(client):
    """Cas limite : réserver exactement le nombre de places restantes
    doit fonctionner (pas d'erreur off-by-one)."""
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Fall Classic', 'club': 'She Lifts', 'places': '12'},
        follow_redirects=True,
    )
    assert response.status_code == 200

    competition = get_competition('Fall Classic')
    club = get_club('She Lifts')
    assert int(competition['numberOfPlaces']) == 1  # 13 - 12
    assert int(club['points']) == 0  # 12 - 12