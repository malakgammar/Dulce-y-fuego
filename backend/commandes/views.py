from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cart, CartItem, Order, OrderItem
from menu.models import Plat

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


class AjouterAuPanierView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, plat_id):
        plat = get_object_or_404(Plat, id=plat_id)
        cart = get_or_create_cart(request)
        quantite = int(request.POST.get('quantite', 1))
        if quantite < 1:
            quantite = 1

        cart_item, created = CartItem.objects.get_or_create(cart=cart, plat=plat)

        if not created:
            cart_item.quantite += quantite
        else:
            cart_item.quantite = quantite

        cart_item.save()
        return redirect('panier')


class PanierView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        cart = get_or_create_cart(request)
        return render(request, 'commandes/panier.html', {'cart': cart})


class SupprimerItemView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
        return redirect('panier')


class MettreAJourQuantiteView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)
        quantite = int(request.POST.get('quantite', 1))

        if quantite < 1:
            item.delete()
        else:
            item.quantite = quantite
            item.save()

        return redirect('panier')


class ConfirmerCommandeView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return redirect('panier')
        return render(request, 'commandes/confirmer.html', {'cart': cart})

    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return redirect('panier')

        adresse = request.POST.get('adresse_livraison', '')

        order = Order.objects.create(
            user=request.user,
            adresse_livraison=adresse,
            total=cart.total
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                plat=item.plat,
                quantite=item.quantite,
                prix=item.plat.prix
            )

        cart.items.all().delete()

        return redirect('confirmation', order_id=order.id)


class ConfirmationView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'commandes/confirmation.html', {'order': order})