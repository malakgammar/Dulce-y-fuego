from django.db import models

class Vente(models.Model):
    date = models.DateField(auto_now_add=True)
    categorie = models.CharField(max_length=100)
    nb_ventes = models.IntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Vente {self.date} - {self.categorie}"