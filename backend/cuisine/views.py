from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from commandes.models import Order
from personnel.models import Employe
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
def is_cuisinier(user):
    return hasattr(user, 'employe') and user.employe.poste == 'cuisinier'


@login_required
def cuisine_dashboard(request):
    if not is_cuisinier(request.user):
        return HttpResponseForbidden("Accès refusé")

    commandes_actives = Order.objects.filter(
        statut__in=['en_attente', 'en_preparation']   
    ).order_by('created_at')

    commandes_archivees = Order.objects.filter(
        statut__in=['prete', 'annulee']
    ).order_by('-created_at')

    return render(request, 'cuisine/dashboardC.html', {
        'commandes_actives': commandes_actives,
        'commandes_archivees': commandes_archivees,
    })


@login_required
def cuisine(request):
    employe = get_object_or_404(Employe, user=request.user)

    return render(request, "cuisine/dashboardC.html", {
        "employe": employe
    })

@login_required
def update_status(request, order_id, action):
    if not is_cuisinier(request.user):
        return HttpResponseForbidden("Accès refusé")

    order = get_object_or_404(Order, id=order_id)

    if action == "accept":       
        order.statut = "en_preparation"
    elif action == "finish":
        order.statut = "prete"
    elif action == "cancel":
        order.statut = "annulee"

    order.save()
    return redirect('cuisine_dashboard')

@login_required
def cuisine_order_detail(request, order_id):

    if not is_cuisinier(request.user):
        return HttpResponseForbidden("Accès refusé")

    order = get_object_or_404(Order, id=order_id)

    return render(request, 'cuisine/detail.html', {
        'order': order
    })

@login_required 
def update_profileC(request):
    if request.method == "POST":
        user = request.user

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        password = request.POST.get("password")
        if password:
            user.set_password(password)
            user.save()

            update_session_auth_hash(request, user) 

        user.save()

        try:
            employe = Employe.objects.get(user=user)
            employe.prenom = user.first_name
            employe.nom = user.last_name
            employe.save()
        except Employe.DoesNotExist:
            pass

        messages.success(request, "Profil mis à jour", extra_tags="profile")
        return redirect("cuisine_dashboard")

    return redirect("cuisine_dashboard")