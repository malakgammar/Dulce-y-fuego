from django.contrib import admin
from .models import Categorie, Plat

admin.site.site_header = "Dulce y Fuego "
admin.site.site_title = "Administration"
admin.site.index_title = "Gestion du restaurant"

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nom',)} # slug auto-rempli 

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix')
    list_filter = ('categorie',)
    search_fields = ('nom',)

