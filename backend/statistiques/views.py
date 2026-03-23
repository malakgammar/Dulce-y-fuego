from django.shortcuts import render
from django.views import View

class StatListView(View):
    def get(self, request):
        return render(request, 'statistiques/dashboard.html', {})