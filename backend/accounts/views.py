# accounts/views.py
from urllib import request

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
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')  # rôle choisi UI

        user = authenticate(request, username=username, password=password)

        if user:
            real_role = get_user_role(user)

            # ❌ rôle incorrect
            if selected_role and selected_role != real_role:
                error = " Rôle incorrect. Veuillez sélectionner votre vrai profil."
                return render(request, 'accounts/login.html', {'error': error})

            # ✅ login OK
            login(request, user)

            redirects = {
                'client': '/',
                'serveur': '/serveur/',
                'cuisinier': '/cuisine/',
                'manager': '/manager/',
                'admin': '/admin/',
            }

            return redirect(redirects.get(real_role, '/'))

        else:
            error = " Identifiant ou mot de passe incorrect."

    return render(request, 'accounts/login.html', {'error': error})

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

        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {'error': 'Utilisateur déjà existe'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            address=address
        )

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