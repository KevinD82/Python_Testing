"""Tests unitaires - route /book. Branche bug/book-route-crash."""


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
    assert "introuvable".encode('utf-8') in response.data.lower()