from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
import json
import openpyxl
from reportlab.platypus import SimpleDocTemplate, Table
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from commandes.models import Order, OrderItem
from menu.models import Plat, Categorie
from personnel.models import Employe
from users.models import CustomUser
# 🔐 Vérification manager
def is_manager(user):
    return hasattr(user, 'employe') and user.employe.poste == 'manager'


@user_passes_test(is_manager)
def dashboard(request):

    # 📅 FILTRE (day / week / month / year)
    period = request.GET.get('period', 'day')
    status = request.GET.get('status')

    commandes_qs = Order.objects.all().order_by('-created_at')

    if status:
        commandes_qs = commandes_qs.filter(statut=status)

    if period == 'week':
        truncate = TruncWeek('created_at')
    elif period == 'month':
        truncate = TruncMonth('created_at')
    elif period == 'year':
        truncate = TruncYear('created_at')
    else:
        truncate = TruncDay('created_at')

    # 💰 VENTES (CA réel)
    ventes = (
        Order.objects.filter(statut='servie')
        .annotate(period=truncate)
        .values('period')
        .annotate(total=Sum('total'))
        .order_by('period')
    )

    # 📦 COMMANDES (option chart 2)
    commandes_par_periode = (
        Order.objects
        .annotate(period=truncate)
        .values('period')
        .annotate(count=Count('id'))
        .order_by('period')
    )

    # 🍽️ TOP PLATS

    top_plats = []

    for plat in Plat.objects.all():
        total = OrderItem.objects.filter(plat=plat).aggregate(
            total=Sum('quantite')
        )['total'] or 0   # 👈 IMPORTANT : 0 si jamais commandé

        top_plats.append({
            'nom': plat.nom,
            'total': total
        })

    # 🔥 tri optionnel (les plus vendus en premier)
    top_plats = sorted(top_plats, key=lambda x: x['total'], reverse=True)

    # 💰 TOTAL REVENUE GLOBAL
    total_revenue = Order.objects.filter(statut='servie').aggregate(
        total=Sum('total')
    )['total'] or 0

    context = {
        # KPI
        'total_revenue': total_revenue,
        'commandes': Order.objects.count(),

        # 📊 CHART VENTES
        'labels': json.dumps([str(v['period']) for v in ventes]),
        'data': json.dumps([float(v['total']) for v in ventes]),

        # 📊 CHART COMMANDES
        'labels_cmd': json.dumps([str(c['period']) for c in commandes_par_periode]),
        'data_cmd': json.dumps([c['count'] for c in commandes_par_periode]),

        # 🍽️ TOP PLATS
        'plats_labels': json.dumps([p['nom'] for p in top_plats]),
        'plats_data': json.dumps([p['total'] for p in top_plats]),

        # CRUD DATA
        'employes': Employe.objects.all(),
        'categories': Categorie.objects.all(),
        'plats': Plat.objects.all(),

        # 🔥 FILTER STATE
        'period': period,
        'commandes_list': commandes_qs,
    }

    return render(request, 'manager/dashboard.html', context)


# ===================== EMPLOYE =====================
@user_passes_test(is_manager)
def employe_add(request):
    if request.method == "POST":
        Employe.objects.create(
            nom=request.POST.get('nom'),
            prenom=request.POST.get('prenom'),
            poste=request.POST.get('poste'),
            telephone=request.POST.get('telephone')
        )
    return redirect('manager_dashboard')


@user_passes_test(is_manager)
def employe_delete(request, id):
    Employe.objects.get(id=id).delete()
    return redirect('manager_dashboard')

@user_passes_test(is_manager)
def employe_update_role(request, id):
    employe = get_object_or_404(Employe, id=id)

    if request.method == "POST":
        employe.poste = request.POST.get('poste')
        employe.save()

    return redirect('manager_dashboard')


@user_passes_test(is_manager)
def employe_add(request):
    if request.method == "POST":

        # 1. créer user (compte login)
        user = CustomUser.objects.create(
            username=request.POST.get('username'),
            password=make_password(request.POST.get('password')),
            first_name=request.POST.get('prenom'),
            last_name=request.POST.get('nom'),
            is_staff=True  # accès admin Django si besoin
        )

        # 2. créer employé lié
        Employe.objects.create(
            user=user,
            nom=request.POST.get('nom'),
            prenom=request.POST.get('prenom'),
            poste=request.POST.get('poste'),
            telephone=request.POST.get('telephone')
        )

    return redirect('manager_dashboard')
# ===================== CATEGORIE =====================
@user_passes_test(is_manager)
def categorie_add(request):
    if request.method == "POST":
        Categorie.objects.create(
            nom=request.POST.get('nom'),
            slug=request.POST.get('slug')
        )
    return redirect('manager_dashboard')


@user_passes_test(is_manager)
def categorie_delete(request, id):
    Categorie.objects.get(id=id).delete()
    return redirect('manager_dashboard')

@user_passes_test(is_manager)
def categorie_update(request, id):
    categorie = get_object_or_404(Categorie, id=id)

    if request.method == "POST":
        categorie.nom = request.POST.get('nom')
        categorie.slug = request.POST.get('slug')
        categorie.save()
        return redirect('manager_dashboard')

    return render(request, 'manager/edit_categorie.html', {
        'categorie': categorie
    })
# ===================== PLAT =====================
@user_passes_test(is_manager)
def plat_add(request):
    if request.method == "POST":
        categorie = Categorie.objects.get(id=request.POST.get('categorie'))

        Plat.objects.create(
            nom=request.POST.get('nom'),
            description=request.POST.get('description'),
            prix=request.POST.get('prix'),
            stock=request.POST.get('stock'),
            categorie=categorie,
            image=request.FILES.get('image')
        )
    return redirect('manager_dashboard')


@user_passes_test(is_manager)
def plat_delete(request, id):
    Plat.objects.get(id=id).delete()
    return redirect('manager_dashboard')

@user_passes_test(is_manager)
def plat_update(request, id):
    plat = get_object_or_404(Plat, id=id)

    if request.method == "POST":
        plat.nom = request.POST.get('nom')
        plat.description = request.POST.get('description')
        plat.prix = request.POST.get('prix')
        plat.stock = request.POST.get('stock')

        categorie_id = request.POST.get('categorie')

        if categorie_id:
            try:
                plat.categorie = Categorie.objects.get(id=categorie_id)
            except Categorie.DoesNotExist:
                plat.categorie = None 

        if request.FILES.get('image'):
            plat.image = request.FILES.get('image')

        plat.save()
        return redirect('manager_dashboard')

    return redirect('manager_dashboard')
# ===================== COMMANDE =====================
@user_passes_test(is_manager)
def commande_update(request, id):
    commande = get_object_or_404(Order, id=id)
    if request.method == "POST":
        commande.statut = request.POST.get('statut')
        commande.save()
    return redirect('manager_dashboard')


# ===================== EXPORT EXCEL =====================
@user_passes_test(is_manager)
def export_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["ID", "Total", "Statut"])

    for cmd in Order.objects.all():
        ws.append([cmd.id, float(cmd.total), cmd.statut])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=commandes.xlsx'
    wb.save(response)

    return response


# ===================== EXPORT PDF =====================
@user_passes_test(is_manager)
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport.pdf"'

    doc = SimpleDocTemplate(response)

    data = [["ID", "Total", "Statut"]]
    for cmd in Order.objects.all():
        data.append([cmd.id, cmd.total, cmd.statut])

    table = Table(data)
    doc.build([table])

    return response