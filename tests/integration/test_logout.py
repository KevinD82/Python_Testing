"""Tests d'intégration - déconnexion. Branche test/coverage-improvements."""


def test_logout_redirects_to_index(client):
    # Effectue une requête GET sur la route de déconnexion
    response = client.get('/logout')
    # Vérifie la redirection (302) vers la page d'accueil
    assert response.status_code == 302
    assert response.location == '/'