"""Tests unitaires - réservation de places. Branche bug/purchase-places-limits."""


def get_competition(name):
    # Helper : extrait la compétition correspondante de l'état global du serveur
    from server import competitions
    return next(c for c in competitions if c['name'] == name)


def get_club(name):
    # Helper : extrait le club correspondant de l'état global du serveur
    from server import clubs
    return next(c for c in clubs if c['name'] == name)


def test_valid_booking_deducts_points_and_places(client):
    # Réservation nominale de 5 places
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '5'},
        follow_redirects=True,
    )
    # Vérifie le succès HTTP et le message de confirmation
    assert response.status_code == 200
    assert b"complete" in response.data.lower() or b"confirm" in response.data.lower()

    # Valide la déduction effective en mémoire (25 - 5 = 20 places / 13 - 5 = 8 points)
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
    # Modification temporaire de la capacité pour cibler la règle des places dispo
    competition = get_competition('Spring Festival')
    competition['numberOfPlaces'] = 5  # simulation d'un stock faible

    # Tentative de réservation de 8 places (supérieur au stock de 5)
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '8'},
        follow_redirects=True,
    )
    # Vérifie que le message traite spécifiquement du manque de places
    assert response.status_code == 200
    assert "disponibles".encode('utf-8') in response.data.lower()  # noqa: UP012

    # Vérifie qu'aucun changement n'a été appliqué aux données
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 5
    assert int(club['points']) == 13


def test_cannot_book_more_than_twelve_places(client):
    # Tentative d'achat de 13 places (dépassement de la limite de 12 par transaction)
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Simply Lift', 'places': '13'},
        follow_redirects=True,
    )
    # Vérifie le rejet par l'application
    assert response.status_code == 200
    assert b"12" in response.data

    # Vérifie que l'état initial reste inchangé
    competition = get_competition('Spring Festival')
    club = get_club('Simply Lift')
    assert int(competition['numberOfPlaces']) == 25
    assert int(club['points']) == 13


def test_cannot_book_more_places_than_club_points(client):
    # 'Iron Temple' (4 points) tente de réserver 5 places
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Spring Festival', 'club': 'Iron Temple', 'places': '5'},
        follow_redirects=True,
    )
    # Vérifie l'avertissement relatif au manque de points
    assert response.status_code == 200
    assert b"point" in response.data.lower()

    # Vérifie que l'état reste bloqué
    competition = get_competition('Spring Festival')
    club = get_club('Iron Temple')
    assert int(competition['numberOfPlaces']) == 25
    assert int(club['points']) == 4


def test_booking_exact_available_places_succeeds(client):
    # Réservation à la limite exacte autorisée (12 places)
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Fall Classic', 'club': 'She Lifts', 'places': '12'},
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Vérification des totaux restants (13 - 12 = 1 place / 12 - 12 = 0 point)
    competition = get_competition('Fall Classic')
    club = get_club('She Lifts')
    assert int(competition['numberOfPlaces']) == 1
    assert int(club['points']) == 0


def test_purchase_with_unknown_club_or_competition_does_not_crash(client):
    """Couvre le garde-fou club/compétition inconnu de purchasePlaces
    (lignes non testées jusqu'ici)."""
    # Soumission avec un nom de compétition totalement inconnu
    response = client.post(
        '/purchasePlaces',
        data={'competition': 'Competition Inconnue', 'club': 'Simply Lift', 'places': '1'},
    )
    # Vérifie la redirection de sécurité vers la racine
    assert response.status_code == 302
    assert response.location == '/'