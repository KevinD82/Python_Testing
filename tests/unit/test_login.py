"""
Tests unitaires pour la fonctionnalité de connexion (login) des secrétaires
de club - branche feature/tests-login.

Le code de showSummary a été corrigé : un email inconnu ne fait plus
planter l'application, il redirige (302) vers l'accueil avec un message
flash. Ces tests suivent donc la redirection avec follow_redirects=True
pour vérifier le résultat final vu par l'utilisateur.

Happy path : email valide -> page de bienvenue avec le club et les compétitions.
Sad path   : email invalide/inexistant -> pas de crash, redirection + message
             d'erreur, retour à la page d'accueil.
"""


def test_index_page_loads(client):
    """La page d'accueil doit se charger correctement (GET /)."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"email" in response.data.lower()


def test_login_with_valid_email_shows_welcome_page(client):
    """Un email connu (Simply Lift) doit afficher la page de bienvenue
    avec le club et la liste des compétitions."""
    response = client.post(
        '/showSummary',
        data={'email': 'john@simplylift.co'},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"john@simplylift.co" in response.data
    assert b"Spring Festival" in response.data


def test_login_with_unknown_email_redirects_with_error_message(client):
    """Bug critique signale par la QA (deja corrige) : un email inconnu
    ne doit plus faire planter l'application. Il doit rediriger vers
    l'accueil (302) avec un message d'erreur flash."""
    response = client.post(
        '/showSummary',
        data={'email': 'inconnu@example.com'},
    )
    assert response.status_code == 302
    assert response.location == '/'

    # On suit la redirection pour verifier le message affiche a l'utilisateur
    followed = client.post(
        '/showSummary',
        data={'email': 'inconnu@example.com'},
        follow_redirects=True,
    )
    assert followed.status_code == 200
    assert b"introuvable" in followed.data


def test_login_with_missing_email_field_does_not_crash(client):
    """Si le champ email est absent du formulaire, l'application
    ne doit pas planter avec une erreur 500 (KeyError)."""
    response = client.post('/showSummary', data={})
    assert response.status_code != 500


def test_login_with_empty_email_redirects_with_error_message(client):
    """Un email vide doit être traité comme un email inconnu :
    redirection avec message d'erreur, pas de crash."""
    response = client.post('/showSummary', data={'email': ''})
    assert response.status_code == 302
    assert response.location == '/'