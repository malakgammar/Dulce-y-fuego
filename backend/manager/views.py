import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from commandes.models import Order, OrderItem
from menu.models import Plat, Categorie
from personnel.models import Employe
from users.models import CustomUser


def is_manager(user):
    return hasattr(user, 'employe') and user.employe.poste == 'manager'


@login_required
def manager_dashboard(request):
    if not is_manager(request.user):
        return redirect('/login/')  # ou une page d'erreur "Accès refusé"

    # ── PÉRIODE ──
    period = request.GET.get('period', 'week')
    now = timezone.now()

    if period == 'day':
        debut = now - timedelta(days=1)
    elif period == 'month':
        debut = now - timedelta(days=30)
    elif period == 'year':
        debut = now - timedelta(days=365)
    else:  # week
        debut = now - timedelta(days=7)

    orders_periode = Order.objects.filter(created_at__gte=debut)

    # ── LABELS + DATA pour graphique ventes ──
    days = 7 if period in ['day', 'week'] else (30 if period == 'month' else 12)
    labels = []
    data_ventes = []
    for i in range(days - 1, -1, -1):
        if period == 'year':
            d = now - timedelta(days=i * 30)
            label = d.strftime('%b')
        else:
            d = now - timedelta(days=i)
            label = d.strftime('%d/%m')
        labels.append(label)
        total = Order.objects.filter(
            created_at__date=d.date(),
            statut='servie'
        ).aggregate(s=Sum('total'))['s'] or 0
        data_ventes.append(float(total))





    # ── GRAPH (tous les plats) ──
    plats_qs = Plat.objects.annotate(
        total=Sum('commande_items__quantite')
    )

    plats_labels = []
    plats_data = []

    for p in plats_qs:
        plats_labels.append(p.nom)
        plats_data.append(p.total or 0)


    # ── TOP PLATS (>10) ──
    top_plats_qs = (
        Plat.objects
        .annotate(total=Sum('commande_items__quantite'))
        .filter(total__gt=10)
        .values('nom', 'total')
        .order_by('-total')
    )

    # ⚠️ toujours transformer en liste (important)
    top_plats_qs = list(top_plats_qs)

    # format pour HTML
    top_plats_qs = [
        {'plat__nom': p['nom'], 'total': p['total']}
        for p in top_plats_qs
    ]

    # limiter top 5
    top_plats_qs = top_plats_qs[:5]

    # éviter division par 0
    max_val = top_plats_qs[0]['total'] if top_plats_qs else 1

    top_plats = [
        {**p, 'pct': round(p['total'] / max_val * 100)}
        for p in top_plats_qs
]

    # ── STATUTS pour donut ──
    statut_data = [
        Order.objects.filter(statut='en_attente').count(),
        Order.objects.filter(statut='en_preparation').count(),
        Order.objects.filter(statut='servie').count(),
        Order.objects.filter(statut='annulee').count(),
    ]

    # ── FILTRE COMMANDES ──
    statut_filtre = request.GET.get('status', '')

    if statut_filtre:
        commandes_list = Order.objects.filter(statut=statut_filtre).order_by('-created_at')
    else:
        commandes_list = Order.objects.all().order_by('-created_at')
    context = {
        # stats globales
        'total_revenue': Order.objects.filter(statut='servie').aggregate(s=Sum('total'))['s'] or 0,
        'commandes': Order.objects.count(),
        'period': period,

        # charts
        'labels':       labels,
        'data':         data_ventes,
        'plats_labels': plats_labels,
        'plats_data':   plats_data,
        'statut_data':  statut_data,
        'top_plats':    top_plats,

        # listes
        'commandes_list': commandes_list,
        'statut_filtre':  statut_filtre,
        'employes':       Employe.objects.all(),
        'plats':          Plat.objects.select_related('categorie').all(),
        'categories':     Categorie.objects.all(),
    }
    return render(request, 'manager/dashboardM.html', context)


# ══════════════════════════
# EMPLOYÉS
# ══════════════════════════

@login_required
def employe_add(request):
    if request.method == 'POST':
        username  = request.POST['username']
        password  = request.POST['password']
        nom       = request.POST.get('nom', '')
        prenom    = request.POST.get('prenom', '')
        telephone = request.POST.get('telephone', '')
        poste     = request.POST.get('poste', 'serveur')

        user = CustomUser.objects.create_user(username=username, password=password)
        Employe.objects.create(
            user=user, nom=nom, prenom=prenom,
            poste=poste, telephone=telephone
        )
        messages.success(request, f'Employé {prenom} {nom} créé.')
    return redirect('/manager/?page=employes')

@login_required
def employe_delete(request, emp_id):
    emp = get_object_or_404(Employe, id=emp_id)
    if emp.user:
        emp.user.delete()
    else:
        emp.delete()
    messages.success(request, 'Employé supprimé.')
    return redirect('/manager/?page=employes')


@login_required
def employe_update_role(request, emp_id):
    emp = get_object_or_404(Employe, id=emp_id)
    if request.method == 'POST':
        emp.poste     = request.POST.get('poste', emp.poste)
        emp.telephone = request.POST.get('telephone', emp.telephone)
        emp.save()
        messages.success(request, 'Employé mis à jour.')
    return redirect('/manager/?page=employes')


# ══════════════════════════
# CATÉGORIES
# ══════════════════════════

@login_required
def categorie_add(request):
    if request.method == 'POST':
        Categorie.objects.create(
            nom=request.POST['nom'],
            slug=request.POST['slug']
        )
        messages.success(request, 'Catégorie ajoutée.')
    return redirect('/manager/?page=categories')


@login_required
def categorie_update(request, cat_id):
    cat = get_object_or_404(Categorie, id=cat_id)
    if request.method == 'POST':
        cat.nom  = request.POST.get('nom', cat.nom)
        cat.slug = request.POST.get('slug', cat.slug)
        cat.save()
        messages.success(request, 'Catégorie mise à jour.')
    return redirect('/manager/?page=categories')


@login_required
def categorie_delete(request, cat_id):
    get_object_or_404(Categorie, id=cat_id).delete()
    messages.success(request, 'Catégorie supprimée.')
    return redirect('/manager/?page=categories')


# ══════════════════════════
# PLATS
# ══════════════════════════

@login_required
def plat_add(request):
    if request.method == 'POST':
        Plat.objects.create(
            nom=request.POST['nom'],
            prix=request.POST['prix'],
            stock=request.POST.get('stock', 0),
            description=request.POST.get('description', ''),
            categorie=Categorie.objects.get(id=request.POST['categorie']),
            image=request.FILES.get('image'),
        )
        messages.success(request, 'Plat ajouté.')
    return redirect('/manager/?page=plats')


@login_required
def plat_update(request, plat_id):
    plat = get_object_or_404(Plat, id=plat_id)
    if request.method == 'POST':
        plat.nom         = request.POST.get('nom', plat.nom)
        plat.prix        = request.POST.get('prix', plat.prix)
        plat.stock       = request.POST.get('stock', plat.stock)
        plat.description = request.POST.get('description', plat.description)
        cat_id           = request.POST.get('categorie')
        if cat_id:
            plat.categorie = Categorie.objects.get(id=cat_id)
        if 'image' in request.FILES:
            plat.image = request.FILES['image']
        plat.save()
        messages.success(request, 'Plat mis à jour.')
    return redirect('/manager/?page=plats')


@login_required
def plat_delete(request, plat_id):
    get_object_or_404(Plat, id=plat_id).delete()
    messages.success(request, 'Plat supprimé.')
    return redirect('/manager/?page=plats')


# ══════════════════════════
# EXPORTS CSV
# ══════════════════════════

@login_required
def export_commandes(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="commandes.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Client', 'Total', 'Statut', 'Date'])
    
    for o in Order.objects.select_related('user').all().order_by('-created_at'):
        try:
            username = o.user.username if o.user_id else '—'
        except Exception:
            username = '—'
        writer.writerow([
            o.id,
            username,
            o.total,
            o.statut,
            o.created_at.strftime('%d/%m/%Y %H:%M')
        ])
    return response


@login_required
def export_employes(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Poste', 'Téléphone', 'Date embauche'])
    for e in Employe.objects.all():
        writer.writerow([e.nom, e.prenom, e.poste, e.telephone, e.date_embauche.strftime('%d/%m/%Y')])
    return response


@login_required
def export_plats(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plats.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Catégorie', 'Prix', 'Stock'])
    for p in Plat.objects.select_related('categorie').all():
        writer.writerow([p.nom, p.categorie.nom if p.categorie else '—', p.prix, p.stock])
    return response