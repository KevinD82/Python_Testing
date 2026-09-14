import json
from flask import Flask,render_template,request,redirect,flash,url_for


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
    # Code d'origine (bug) : plantait avec une IndexError si le club ou
    # la compétition ne correspondait à aucune entrée existante.
    # foundClub = [c for c in clubs if c['name'] == club][0]
    # foundCompetition = [c for c in competitions if c['name'] == competition][0]
    # if foundClub and foundCompetition:
    #     return render_template('booking.html',club=foundClub,competition=foundCompetition)
    # else:
    #     flash("Something went wrong-please try again")
    #     return render_template('welcome.html', club=club, competitions=competitions)

    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    if not foundClub or not foundCompetition:
        flash("Compétition ou club introuvable.")
        return redirect(url_for('index'))

    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    # Code d'origine (bugs) : aucune vérification des places disponibles,
    # aucune limite de 12 places, aucune vérification des points, et les
    # points n'étaient jamais déduits.
    # competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    # club = [c for c in clubs if c['name'] == request.form['club']][0]
    # placesRequired = int(request.form['places'])
    # competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    # flash('Great-booking complete!')
    # return render_template('welcome.html', club=club, competitions=competitions)

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