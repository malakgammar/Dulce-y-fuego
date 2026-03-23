from django.shortcuts import render
from django.views import View

class CommandeListView(View):
    def get(self, request):
        return render(request, 'commandes/commandeList.html', {})