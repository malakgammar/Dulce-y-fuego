from django.db import models

from backend import settings

class Employe(models.Model):
    POSTES = [
        ('cuisinier', 'Cuisinier'),
        ('serveur', 'Serveur'),
        ('caissier', 'Caissier'),
        ('manager', 'Manager'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    poste = models.CharField(max_length=20, choices=POSTES)
    telephone = models.CharField(max_length=20)
    date_embauche = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"