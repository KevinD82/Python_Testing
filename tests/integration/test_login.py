"""Tests d'intégration - connexion (login). Branche fix/login-crash."""


def test_index_page_loads(client):
    # Charge la page d'accueil (GET /)
    response = client.get('/')
    # Vérifie que le code HTTP est 200 et que le formulaire e-mail est présent
    assert response.status_code == 200
    assert b"email" in response.data.lower()


def test_login_with_valid_email_shows_welcome_page(client):
    # Tente une connexion avec l'e-mail d'un secrétaire connu
    response = client.post(
        '/showSummary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
    # Vérifie la redirection vers le tableau de bord avec les données associées
    assert response.status_code == 200
    assert b"john@simplylift.co" in response.data
    assert b"Spring Festival" in response.data


def test_login_with_unknown_email_redirects_with_error_message(client):
    # Tente la connexion avec un e-mail inexistant et vérifie le statut 302
    response = client.post('/showSummary', data={'email': 'inconnu@example.com'})
    assert response.status_code == 302
    assert response.location == '/'

    # Rejoue la requête en suivant la redirection pour inspecter le message affiché
    followed = client.post(
        '/showSummary',
        data={'email': 'inconnu@example.com'},
        follow_redirects=True,
    )
    # Assure que le message d'erreur est affiché sur la page d'accueil
    assert followed.status_code == 200
    assert b"introuvable" in followed.data


def test_login_with_missing_email_field_does_not_crash(client):
    # Soumet le formulaire sans inclure le champ 'email'
    response = client.post('/showSummary', data={})
    # S'assure que l'application ne lève pas une exception 500 (KeyError)
    assert response.status_code != 500


def test_login_with_empty_email_redirects_with_error_message(client):
    # Envoie une valeur d'e-mail vide
    response = client.post('/showSummary', data={'email': ''})
    # Vérifie la redirection immédiate vers l'accueil
    assert response.status_code == 302
    assert response.location == '/'


def test_welcome_page_hides_past_competitions(client):
    """Une compétition passée ne doit plus apparaître dans la liste du secrétaire."""
    from server import competitions
    competition = next(c for c in competitions if c['name'] == 'Spring Festival')
    competition['date'] = "2020-01-01 10:00:00"

    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b"Spring Festival" not in response.data
    assert b"Fall Classic" in response.data