from django.urls import path
from .views import (
    AjouterAuPanierView, PanierView,
    SupprimerItemView, MettreAJourQuantiteView,
    ConfirmerCommandeView, ConfirmationView
)

urlpatterns = [

    path('', PanierView.as_view(), name='panier'),
    path('ajouter/<int:plat_id>/', AjouterAuPanierView.as_view(), name='ajouter_panier'),
    path('supprimer/<int:item_id>/', SupprimerItemView.as_view(), name='supprimer_item'),
    path('update/<int:item_id>/', MettreAJourQuantiteView.as_view(), name='update_item'),
    path('confirmer/', ConfirmerCommandeView.as_view(), name='confirmer_commande'),
    path('confirmation/<int:order_id>/', ConfirmationView.as_view(), name='confirmation'),
]