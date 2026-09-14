"""Tests unitaires - tableau public des points. Branche feature/points-board."""


def test_points_board_accessible_without_login(client):
    response = client.get('/points')
    assert response.status_code == 200


def test_points_board_lists_all_clubs_with_their_points(client):
    response = client.get('/points')
    assert response.status_code == 200
    assert b"Simply Lift" in response.data
    assert b"13" in response.data
    assert b"Iron Temple" in response.data
    assert b"4" in response.data
    assert b"She Lifts" in response.data
    assert b"12" in response.data


def test_points_board_has_no_booking_or_purchase_links(client):
    response = client.get('/points')
    assert b"/purchasePlaces" not in response.data
    assert b"/book/" not in response.data