from django.shortcuts import render
from django.views import View

class PersonnelListView(View):
    def get(self, request):
        return render(request, 'personnel/personnelList.html', {})