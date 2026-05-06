from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from personnel.models import Employe
from commandes.models import Order
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def serveur_dashboard(request):
    if not hasattr(request.user, 'employe') or request.user.employe.poste != "serveur":
        return redirect("login")

    commandes_pretes = Order.objects.filter(statut="prete").order_by("-id")

    commandes_servies = Order.objects.filter(statut="servie").order_by("-updated_at")

    return render(request, "serveur/dashboardS.html", {
        "commandes_pretes": commandes_pretes,
        "commandes_servies": commandes_servies
    })

@login_required
def servir_commande(request, order_id):
    commande = get_object_or_404(Order, id=order_id)

    commande.statut = "servie"
    commande.save()

    messages.success(request, f"Commande #{commande.id} servie avec succès", extra_tags="commande")
    return redirect("serveur_dashboard")

    
@login_required 
def update_profile(request):
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
        return redirect("serveur_dashboard")

    return redirect("serveur_dashboard")