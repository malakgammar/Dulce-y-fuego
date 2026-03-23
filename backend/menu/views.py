from django.shortcuts import render
from django.views import View

class MenuListView(View):
    def get(self, request):
        return render(request, 'menu/menulist.html', {})