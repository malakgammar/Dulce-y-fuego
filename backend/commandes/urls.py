from django.urls import path
from .views import CommandeListView

urlpatterns = [
    path('', CommandeListView.as_view(), name='commandes'),
]