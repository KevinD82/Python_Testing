"""Tests unitaires - déconnexion. Branche test/coverage-improvements."""


def test_logout_redirects_to_index(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.location == '/'