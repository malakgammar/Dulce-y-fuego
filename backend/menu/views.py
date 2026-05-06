from django.views.generic import ListView
from .models import Plat, Categorie
from django.contrib.auth.decorators import login_required

class MenuListView(ListView):
    model = Plat
    template_name = 'menu/menuList.html'
    context_object_name = 'plats'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        return context

@login_required
def plats_list(request):
    plats = Plat.objects.all()
    return render(request, 'menu/plats_list.html', {'plats': plats})

@login_required
def add_plat(request):
    categories = Categorie.objects.all()

    if request.method == 'POST':
        Plat.objects.create(
            nom=request.POST['nom'],
            description=request.POST['description'],
            prix=request.POST['prix'],
            stock=request.POST['stock'],
            categorie_id=request.POST['categorie'],
            image=request.FILES.get('image')
        )
        return redirect('plats_list')

    return render(request, 'menu/add_plat.html', {'categories': categories})


@login_required
def edit_plat(request, id):
    plat = get_object_or_404(Plat, id=id)
    categories = Categorie.objects.all()

    if request.method == 'POST':
        plat.nom = request.POST['nom']
        plat.description = request.POST['description']
        plat.prix = request.POST['prix']
        plat.stock = request.POST['stock']
        plat.categorie_id = request.POST['categorie']

        if request.FILES.get('image'):
            plat.image = request.FILES.get('image')

        plat.save()
        return redirect('plats_list')

    return render(request, 'menu/edit_plat.html', {
        'plat': plat,
        'categories': categories
    })

@login_required
def delete_plat(request, id):
    plat = get_object_or_404(Plat, id=id)
    plat.delete()
    return redirect('plats_list')

def add_categorie(request):
    if request.method == 'POST':
        Categorie.objects.create(
            nom=request.POST['nom'],
            slug=request.POST['slug']
        )
        return redirect('plats_list')

    return render(request, 'menu/add_categorie.html')

def delete_categorie(request, id):
    categorie = get_object_or_404(Categorie, id=id)
    categorie.delete()
    return redirect('plats_list')