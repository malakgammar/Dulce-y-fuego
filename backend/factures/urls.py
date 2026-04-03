from django.urls import path
from .views import generer_facture

urlpatterns = [
    path('facture/<int:order_id>/', generer_facture, name='generer_facture'),
]