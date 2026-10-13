def validateBooking(placesRequired, alreadyBooked, availablePlaces, clubPoints, competitionIsPast):
    if competitionIsPast:
        return "Cette compétition est terminée et ne peut plus être réservée."
    if placesRequired < 1:
        return "Veuillez indiquer un nombre de places positif (au moins 1)."
    if alreadyBooked + placesRequired > 12:
        return "Vous ne pouvez pas réserver plus de 12 places par compétition."
    if placesRequired > availablePlaces:
        return "Il ne reste pas assez de places disponibles pour cette compétition."
    if placesRequired > clubPoints:
        return "Votre club n'a pas assez de points pour réserver ce nombre de places."
    return None