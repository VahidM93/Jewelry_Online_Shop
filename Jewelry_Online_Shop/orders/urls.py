from django.urls import path
from . import views

urlpatterns = [
    path('detail/', views.cart_detail, name='cart_detail'),
]