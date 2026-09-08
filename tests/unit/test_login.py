def test_index_status_code(client):
    """Happy Path: Vérifie que la page d'accueil (GET '/') s'affiche correctement."""
    response = client.get('/')
    assert response.status_code == 200


def test_show_summary_valid_email(client):
    """Happy Path: Vérifie la connexion réussie avec un e-mail valide présent dans la base."""
    response = client.post(
        '/showSummary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert (
        b'Welcome, john@simplylift.co' in response.data
        or b'Simply Lift' in response.data
    )


def test_show_summary_invalid_email(client):
    """Sad Path: Vérifie la gestion d'erreur lors d'une tentative de connexion avec un e-mail inconnu."""
    response = client.post(
        '/showSummary',
        data={'email': 'inexistant@club.com'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Désolé, cette adresse e-mail est introuvable.".encode() in response.data