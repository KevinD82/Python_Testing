import json
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from booking_rules import maxBookablePlaces, validateBooking

CLUBS_FILE = 'clubs.json'
COMPETITIONS_FILE = 'competitions.json'

def loadClubs():
    with open(CLUBS_FILE, encoding='utf-8') as c:
        return json.load(c)['clubs']


def loadCompetitions():
    with open(COMPETITIONS_FILE, encoding='utf-8') as comps:
        return json.load(comps)['competitions']


def isCompetitionPast(competition):
    date_competition = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S").astimezone()
    return date_competition < datetime.now().astimezone()


def getCompetitionsWithStatus():
    return [{**c, 'isPast': isCompetitionPast(c)} for c in competitions]


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
# Suivi des réservations déjà effectuées, par club et par compétition,
# pour appliquer la limite de 12 places sur le CUMUL (et non sur une
# seule requête). Clé : tuple (nom du club, nom de la compétition).
bookings = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next((c for c in clubs if c['email'] == email), None)

    if not club:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=getCompetitionsWithStatus())


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Compétition ou club introuvable.")
        return redirect(url_for('index'))

    if isCompetitionPast(foundCompetition):
        flash("Cette compétition est terminée et ne peut plus être réservée.")
        return redirect(url_for('index'))
    
    alreadyBooked = bookings.get((foundClub['name'], foundCompetition['name']), 0)
    maxPlaces = maxBookablePlaces(
        alreadyBooked,
        int(foundCompetition['numberOfPlaces']),
        int(foundClub['points']),
    )

    return render_template(
        'booking.html',
        club=foundClub,
        competition=foundCompetition,
        maxPlaces=maxPlaces,
    )


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash("Une erreur est survenue, veuillez réessayer.")
        return redirect(url_for('index'))

    placesRequired = int(request.form['places'])
    alreadyBooked = bookings.get((club['name'], competition['name']), 0)

    errorMessage = validateBooking(
        placesRequired,
        alreadyBooked,
        int(competition['numberOfPlaces']),
        int(club['points']),
        isCompetitionPast(competition),
    )

    if errorMessage:
        flash(errorMessage)
    else:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        bookings[(club['name'], competition['name'])] = alreadyBooked + placesRequired
        flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=getCompetitionsWithStatus())


@app.route('/points')
def points_board():
    """Tableau public et en lecture seule des points de tous les clubs.
    Accessible sans connexion."""
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

