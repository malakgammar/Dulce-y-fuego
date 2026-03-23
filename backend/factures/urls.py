from django.urls import path
from .views import FactureListView

urlpatterns = [
    path('', FactureListView.as_view(), name='factures'),
]