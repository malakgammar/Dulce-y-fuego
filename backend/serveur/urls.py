from django.urls import path
from .views import serveur_dashboard, servir_commande, update_profile

urlpatterns = [
    path('', serveur_dashboard, name='serveur_dashboard'),
    path('servir/<int:order_id>/', servir_commande, name='servir_commande'),
    path('serveur/profile/update/', update_profile, name='update_profile'),
]