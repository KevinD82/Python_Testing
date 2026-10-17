"""Tests d'intégration - route /book. Branche bug/book-route-crash."""


def test_book_with_valid_club_and_competition_shows_booking_page(client):
    # Envoie une requête GET avec des paramètres valides (club et compétition existants)
    response = client.get('/book/Spring Festival/Simply Lift')
    # Vérifie que la page répond 200 et affiche le nom de la compétition
    assert response.status_code == 200
    assert b"Spring Festival" in response.data


def test_book_with_unknown_club_does_not_crash(client):
    # Envoie une requête GET avec un nom de club inexistant dans l'URL
    response = client.get('/book/Spring Festival/Club Inconnu')
    # Vérifie la redirection 302 vers l'accueil au lieu d'un crash 500
    assert response.status_code == 302
    assert response.location == '/'


def test_book_with_unknown_competition_does_not_crash(client):
    # Envoie une requête GET avec une compétition inexistante dans l'URL
    response = client.get('/book/Competition Inconnue/Simply Lift')
    # Vérifie que la route redirige proprement vers la racine
    assert response.status_code == 302
    assert response.location == '/'


def test_book_with_unknown_club_shows_error_message(client):
    # Suit la redirection (follow_redirects=True) suite à un club inconnu
    response = client.get('/book/Spring Festival/Club Inconnu', follow_redirects=True)
    # Vérifie l'affichage du message flash indiquant que l'élément est introuvable
    assert response.status_code == 200
    assert b"introuvable" in response.data.lower()


def test_book_page_refused_for_past_competition(client):
    """La page de réservation ne doit pas s'ouvrir pour une compétition passée."""
    # Force une date passée (reset_data la restaurera après le test)
    from server import competitions
    competition = next(c for c in competitions if c['name'] == 'Spring Festival')
    competition['date'] = "2020-01-01 10:00:00"

    # Une URL tapée à la main sur une compétition passée doit rediriger vers l'accueil
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 302
    assert response.location == '/'

    # Suit la redirection pour vérifier le message affiché
    followed = client.get('/book/Spring Festival/Simply Lift', follow_redirects=True)
    assert "terminée".encode() in followed.data


def test_book_page_limits_input_to_club_points(client):
    # Iron Temple n'a que 4 points : le champ ne doit pas accepter plus de 4 places
    response = client.get('/book/Spring Festival/Iron Temple')
    assert response.status_code == 200
    assert b'min="1"' in response.data
    assert b'max="4"' in response.data


def test_book_page_has_no_form_when_nothing_is_bookable(client):
    # Un club sans points ne doit pas se voir proposer de formulaire
    from server import clubs
    club = next(c for c in clubs if c['name'] == 'Iron Temple')
    club['points'] = 0

    response = client.get('/book/Spring Festival/Iron Temple')
    assert response.status_code == 200
    assert b'name="places"' not in response.data
