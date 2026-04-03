from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=250, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=250, unique=True)

    def __str__(self):
        return self.nom

class Plat(models.Model):
    nom = models.CharField(max_length=250, verbose_name="Nom")
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    stock = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='plats', verbose_name="Catégorie")
    image = models.ImageField(null=True, blank=True, upload_to='menu/')

    def __str__(self):
        return self.nom