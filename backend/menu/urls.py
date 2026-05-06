from django.urls import path
from .views import *

urlpatterns = [
    path('', MenuListView.as_view(), name='menu'),
    path('plats/add/', add_plat, name='add_plat'),
    path('plats/edit/<int:id>/', edit_plat, name='edit_plat'),
    path('plats/delete/<int:id>/', delete_plat, name='delete_plat'),

    path('categorie/add/', add_categorie, name='add_categorie'),
    path('categorie/delete/<int:id>/', delete_categorie, name='delete_categorie'),
]