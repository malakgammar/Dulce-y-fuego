from django.urls import path
from .views import StatListView

urlpatterns = [
    path('', StatListView.as_view(), name='statistiques'),
]