from django.db import models
from users.models import CustomUser
from menu.models import Plat

class Order(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True, blank=True, related_name='factures'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    adresse_livraison = models.TextField(blank=True)

    def __str__(self):
        return f"Commande {self.id}"

    def update_total(self):
        self.total = sum(item.quantite * item.prix for item in self.items.all())
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE, related_name='facture_items')
    quantite = models.PositiveIntegerField(default=1)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite}x {self.plat.nom}"