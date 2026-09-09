"""
Tests unitaires pour le tableau public des points - branche
feature/points-board (phase 2 des spécifications fonctionnelles).

Exigences :
- La page doit être accessible SANS connexion (pas d'email requis).
- Elle doit lister tous les clubs avec leur nombre de points actuel.
- Elle doit être en lecture seule (aucune action de modification
  possible depuis cette page).
"""


def test_points_board_accessible_without_login(client):
    """La page doit être accessible directement, sans passer par
    /showSummary (donc sans email/connexion)."""
    response = client.get('/points')
    assert response.status_code == 200


def test_points_board_lists_all_clubs_with_their_points(client):
    """Chaque club doit apparaître avec son nombre de points actuel."""
    response = client.get('/points')
    assert response.status_code == 200
    assert b"Simply Lift" in response.data
    assert b"13" in response.data
    assert b"Iron Temple" in response.data
    assert b"4" in response.data
    assert b"She Lifts" in response.data
    assert b"12" in response.data


def test_points_board_has_no_booking_or_purchase_links(client):
    """La page doit être strictement en lecture seule : pas de lien
    ou de formulaire permettant de réserver ou modifier des points."""
    response = client.get('/points')
    assert b"/purchasePlaces" not in response.data
    assert b"/book/" not in response.data