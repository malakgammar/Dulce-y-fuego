# Ajoute ces URLs dans ton urls.py principal

from django.urls import path
from . import views   # adapte l'import selon ton app

urlpatterns = [

    # ── DASHBOARD ──
    path('', views.manager_dashboard, name='manager_dashboard'),

    # ── EMPLOYÉS ──
    path('manager/employe/add/',            views.employe_add,          name='employe_add'),
    path('manager/employe/<int:emp_id>/delete/', views.employe_delete,  name='employe_delete'),
    path('manager/employe/<int:emp_id>/role/',   views.employe_update_role, name='employe_update_role'),

    # ── CATÉGORIES ──
    path('manager/categorie/add/',               views.categorie_add,    name='categorie_add'),
    path('manager/categorie/<int:cat_id>/update/', views.categorie_update, name='categorie_update'),
    path('manager/categorie/<int:cat_id>/delete/', views.categorie_delete, name='categorie_delete'),

    # ── PLATS ──
    path('manager/plat/add/',               views.plat_add,    name='plat_add'),
    path('manager/plat/<int:plat_id>/update/', views.plat_update, name='plat_update'),
    path('manager/plat/<int:plat_id>/delete/', views.plat_delete, name='plat_delete'),

    # ── EXPORTS ──
    path('manager/export/commandes/', views.export_commandes, name='manager_export_commandes'),
    path('manager/export/employes/',  views.export_employes,  name='manager_export_employes'),
    path('manager/export/plats/',     views.export_plats,     name='manager_export_plats'),
]