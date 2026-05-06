from django.urls import path
from .views import *

urlpatterns = [
    path('', dashboard, name='manager_dashboard'),

    # 👨‍💼 employes
    path('employe/add/', employe_add, name='employe_add'),
    path('employe/delete/<int:id>/', employe_delete, name='employe_delete'),
    path('employe/update-role/<int:id>/', employe_update_role, name='employe_update_role'),

    # 🗂️ categories
    path('categorie/add/', categorie_add, name='categorie_add'),
    path('categorie/delete/<int:id>/', categorie_delete, name='categorie_delete'),
    path('categorie/update/<int:id>/', categorie_update, name='categorie_update'),
    # 🍽️ plats
    path('plat/add/', plat_add, name='plat_add'),
    path('plat/delete/<int:id>/', plat_delete, name='plat_delete'),
    path('plat/update/<int:id>/', plat_update, name='plat_update'),

    # 📦 commandes
    path('commande/update/<int:id>/', commande_update, name='commande_update'),

    # 📊 export
    path('export/excel/', export_excel, name='export_excel'),
    path('export/pdf/', export_pdf, name='export_pdf'),
]