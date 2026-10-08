import json

from flask import Flask, flash, redirect, render_template, request, url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

def isCompetitionPast(competition):
    date_competition = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S")
    return date_competition < datetime.now()

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
    # Code d'origine (bug) : plantait avec une IndexError si l'email
    # ne correspondait à aucun club.
    # club = [club for club in clubs if club['email'] == request.form['email']][0]
    # return render_template('welcome.html',club=club,competitions=competitions)

    email = request.form['email']
    club = next((c for c in clubs if c['email'] == email), None)

    if not club:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=competitions)


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
    
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash("Une erreur est survenue, veuillez réessayer.")
        return redirect(url_for('index'))

    placesRequired = int(request.form['places'])
    availablePlaces = int(competition['numberOfPlaces'])
    clubPoints = int(club['points'])
    alreadyBooked = bookings.get((club['name'], competition['name']), 0)

    if isCompetitionPast(competition):
        flash("Cette compétition est terminée et ne peut plus être réservée.")
    elif placesRequired < 1:
        flash("Veuillez indiquer un nombre de places positif (au moins 1).")
    elif alreadyBooked + placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places par compétition.")
    elif placesRequired > availablePlaces:
        flash("Il ne reste pas assez de places disponibles pour cette compétition.")
    elif placesRequired > clubPoints:
        flash("Votre club n'a pas assez de points pour réserver ce nombre de places.")
    else:
        competition['numberOfPlaces'] = availablePlaces - placesRequired
        club['points'] = clubPoints - placesRequired
        bookings[(club['name'], competition['name'])] = alreadyBooked + placesRequired
        flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=competitions)


# Fonctionnalité manquante (phase 2) : tableau public des points.
# TODO: Add route for points display

@app.route('/points')
def points_board():
    """Tableau public et en lecture seule des points de tous les clubs.
    Accessible sans connexion."""
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))