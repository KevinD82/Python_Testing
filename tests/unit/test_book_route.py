"""Tests unitaires - route /book. Branche bug/book-route-crash."""


def test_book_with_valid_club_and_competition_shows_booking_page(client):
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200
    assert b"Spring Festival" in response.data


def test_book_with_unknown_club_does_not_crash(client):
    response = client.get('/book/Spring Festival/Club Inconnu')
    assert response.status_code == 302
    assert response.location == '/'


def test_book_with_unknown_competition_does_not_crash(client):
    response = client.get('/book/Competition Inconnue/Simply Lift')
    assert response.status_code == 302
    assert response.location == '/'


def test_book_with_unknown_club_shows_error_message(client):
    response = client.get('/book/Spring Festival/Club Inconnu', follow_redirects=True)
    assert response.status_code == 200
    assert "introuvable".encode('utf-8') in response.data.lower()