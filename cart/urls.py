from django.urls import path
from . import views

urlpatterns = [
    path('', views.Cart_summary, name='cart_summary'),
    path('add/', views.Cart_add, name="cart_add"),
    path('delete/', views.Cart_delete, name="cart_delete"),
    path('update/', views.Cart_update, name="cart_update"),

]
