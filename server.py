import json

from flask import Flask, flash, redirect, render_template, request, url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

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

    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Compétition ou club introuvable.")
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

    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places par compétition.")
    elif placesRequired > availablePlaces:
        flash("Il ne reste pas assez de places disponibles pour cette compétition.")
    elif placesRequired > clubPoints:
        flash("Votre club n'a pas assez de points pour réserver ce nombre de places.")
    else:
        competition['numberOfPlaces'] = availablePlaces - placesRequired
        club['points'] = clubPoints - placesRequired
        flash('Great-booking complete!')

    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))