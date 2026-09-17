"""
Tests de performance Locust - branche test/locust-performance.

Exigences des spécifications fonctionnelles (phase 2) :
- Récupérer une liste de compétitions : < 5 secondes.
- Mettre à jour le total de points (réservation) : < 2 secondes.
- 6 utilisateurs simultanés par défaut (guide de développement, section 5.c).

Lancement :
    locust -f locustfile.py --host=http://127.0.0.1:5000

Puis ouvrir http://localhost:8089 et configurer :
    - Number of users: 6
    - Ramp up: 6
    - Host: http://127.0.0.1:5000
"""

from locust import HttpUser, task, between


class ClubSecretaryUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_competitions_list(self):
        """Connexion + consultation de la liste des compétitions -
        doit répondre en moins de 5 secondes."""
        with self.client.post(
            "/showSummary",
            data={"email": "john@simplylift.co"},
            name="/showSummary (liste des compétitions)",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure(
                    f"Trop lent : {response.elapsed.total_seconds():.2f}s (max attendu : 5s)"
                )

    @task(1)
    def book_places(self):
        """Réservation de places - la mise à jour des points doit
        prendre moins de 2 secondes."""
        with self.client.post(
            "/purchasePlaces",
            data={
                "competition": "Spring Festival",
                "club": "Simply Lift",
                "places": "1",
            },
            name="/purchasePlaces (mise à jour des points)",
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure(
                    f"Trop lent : {response.elapsed.total_seconds():.2f}s (max attendu : 2s)"
                )

    @task(1)
    def view_points_board(self):
        """Consultation du tableau public des points."""
        self.client.get("/points", name="/points (tableau public)")