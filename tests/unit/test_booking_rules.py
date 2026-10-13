"""Tests unitaires - règles de réservation (aucune dépendance à Flask)."""

import pytest

from booking_rules import maxBookablePlaces, validateBooking


def test_valid_booking_returns_none():
    # Réservation nominale : aucune règle violée, donc aucun message d'erreur
    assert validateBooking(3, 0, 25, 13, False) is None


def test_booking_exactly_twelve_places_is_accepted():
    # Cas limite : 12 places est la limite autorisée
    assert validateBooking(12, 0, 25, 20, False) is None


@pytest.mark.parametrize("args, expected_word", [
    ((3, 0, 25, 13, True), "terminée"),     # compétition passée
    ((0, 0, 25, 13, False), "positif"),     # zéro place
    ((-5, 0, 25, 13, False), "positif"),    # nombre négatif
    ((13, 0, 25, 20, False), "12 places"),  # trop de places d'un coup
    ((7, 6, 25, 20, False), "12 places"),   # cumul : 6 + 7 = 13
    ((8, 0, 5, 20, False), "disponibles"),  # plus que les places restantes
    ((5, 0, 25, 4, False), "points"),       # plus que les points du club
])
def test_invalid_booking_returns_matching_message(args, expected_word):
    # Chaque règle violée doit produire son propre message
    message = validateBooking(*args)
    assert message is not None
    assert expected_word in message


def test_past_competition_has_priority_over_other_rules():
    # Si plusieurs règles sont violées, la compétition terminée est signalée en premier
    message = validateBooking(-1, 0, 25, 13, True)
    assert "terminée" in message

@pytest.mark.parametrize("alreadyBooked, availablePlaces, clubPoints, expected", [
    (0, 25, 13, 12),   # la limite de 12 est la plus basse
    (3, 20, 7, 7),     # les points du club sont la limite
    (0, 5, 13, 5),     # les places restantes sont la limite
    (9, 25, 13, 3),    # le cumul déjà réservé réduit le plafond
    (12, 25, 13, 0),   # plafond atteint : rien de plus à réserver
    (0, 0, 13, 0),     # compétition complète
    (0, 25, 0, 0),     # club sans points
])
def test_max_bookable_places(alreadyBooked, availablePlaces, clubPoints, expected):
    # Le plafond est la plus petite des trois limites, sans jamais descendre sous zéro
    assert maxBookablePlaces(alreadyBooked, availablePlaces, clubPoints) == expected