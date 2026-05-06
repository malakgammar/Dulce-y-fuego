from django.urls import path
from .views import cuisine_dashboard, update_profileC, update_status

urlpatterns = [
    path('', cuisine_dashboard, name='cuisine_dashboard'),
    path('update/<int:order_id>/<str:action>/', update_status, name='update_status'),
    path('cuisine/profile/update/', update_profileC, name='update_profileC'),
]