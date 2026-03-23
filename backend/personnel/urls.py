from django.urls import path
from .views import PersonnelListView

urlpatterns = [
    path('', PersonnelListView.as_view(), name='personnel'),
]