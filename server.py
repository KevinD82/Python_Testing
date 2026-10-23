import json
import threading
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from booking_rules import maxBookablePlaces, validateBooking

CLUBS_FILE = 'clubs.json'
COMPETITIONS_FILE = 'competitions.json'

# Lit clubs.json et renvoie la liste des clubs.
def loadClubs():
    with open(CLUBS_FILE, encoding='utf-8') as c:
        return json.load(c)['clubs']


# Lit competitions.json et renvoie la liste des compétitions.
def loadCompetitions():
    with open(COMPETITIONS_FILE, encoding='utf-8') as comps:
        return json.load(comps)['competitions']

bookingLock = threading.RLock()


# Réécrit clubs.json et competitions.json avec l'état actuel (sous verrou).
def saveData():
    with bookingLock:
        with open(CLUBS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'clubs': clubs}, f, indent=4, ensure_ascii=False)
        with open(COMPETITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'competitions': competitions}, f, indent=4, ensure_ascii=False)


# Renvoie True si la date de la compétition est déjà passée.
def isCompetitionPast(competition):
    date_competition = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S").astimezone()
    return date_competition < datetime.now().astimezone()


# Renvoie une copie des compétitions avec 'isPast', sans toucher à l'original (donc pas écrit dans le JSON).
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

# Page d'accueil : formulaire de saisie de l'e-mail.
@app.route('/')
def index():
    return render_template('index.html')

# Connexion par e-mail : affiche les compétitions, ou un message si l'e-mail est inconnu.
@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next((c for c in clubs if c['email'] == email), None)

    if not club:
        flash("Désolé, cette adresse e-mail est introuvable.")
        return redirect(url_for('index'))

    return render_template('welcome.html', club=club, competitions=getCompetitionsWithStatus())


# Page de réservation : refuse si inconnu ou passé, sinon calcule le maximum réservable.
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


# Réserve des places : valide les règles sous verrou, met à jour les données, enregistre, puis réaffiche la page.
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash("Une erreur est survenue, veuillez réessayer.")
        return redirect(url_for('index'))
    

    try:
        placesRequired = int(request.form['places'])
    except (KeyError, ValueError):
        flash("Veuillez saisir un nombre de places valide.")
        return render_template('welcome.html', club=club, competitions=getCompetitionsWithStatus())
    # La vérification et l'enregistrement forment un seul bloc : une réservation à la fois
    with bookingLock:
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
            saveData()
            flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=getCompetitionsWithStatus())


# Tableau public des points de tous les clubs (lecture seule, sans connexion).
@app.route('/points')
def points_board():
    return render_template('points.html', clubs=clubs)


# Déconnexion 
@app.route('/logout')
def logout():
    return redirect(url_for('index'))