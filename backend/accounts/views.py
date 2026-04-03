# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from commandes.models import Cart, Order

User = get_user_model()


def get_user_role(user):
    """Retourne le rôle de l’utilisateur"""
    if user.is_superuser:
        return 'admin'
    try:
        return user.employe.poste  
    except:
        return 'client'  


def login_view(request):
    """Connexion des utilisateurs"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = get_user_role(user)

            if role == 'admin':
                return redirect('/dashboard/')
            elif role == 'serveur':
                return redirect('/commandes/')
            elif role == 'cuisinier':
                return redirect('/cuisine/')
            elif role == 'caissier':
                return redirect('/paiements/')
            elif role == 'manager':
                return redirect('/statistiques/')
            else:
                return redirect('/')
        else:
            return render(request, 'accounts/login.html', {'error': 'Identifiants invalides'})

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def register_view(request):
    """Inscription des clients"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        # Vérifier si l'email existe déjà
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Utilisateur déjà existe'})

        # Création utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )

        # Connexion auto
        login(request, user)
        return redirect('/')

    return render(request, 'accounts/register.html')


@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.save()
        return redirect('profile')

    commandes = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {
        'commandes': commandes
    })