"""Tests unitaires - connexion (login). Branche fix/login-crash."""


def test_index_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"email" in response.data.lower()


def test_login_with_valid_email_shows_welcome_page(client):
    response = client.post(
        '/showSummary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"john@simplylift.co" in response.data
    assert b"Spring Festival" in response.data


def test_login_with_unknown_email_redirects_with_error_message(client):
    response = client.post('/showSummary', data={'email': 'inconnu@example.com'})
    assert response.status_code == 302
    assert response.location == '/'

    followed = client.post(
        '/showSummary',
        data={'email': 'inconnu@example.com'},
        follow_redirects=True,
    )
    assert followed.status_code == 200
    assert "introuvable".encode('utf-8') in followed.data


def test_login_with_missing_email_field_does_not_crash(client):
    response = client.post('/showSummary', data={})
    assert response.status_code != 500


def test_login_with_empty_email_redirects_with_error_message(client):
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302
    assert response.location == '/'