from django.views.generic import ListView
from .models import Plat, Categorie

class MenuListView(ListView):
    model = Plat
    template_name = 'menu/menuList.html'
    context_object_name = 'plats'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        return context
        