from django.shortcuts import render
from django.views import View

class FactureListView(View):
    def get(self, request):
        return render(request, 'factures/factureList.html', {})