from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    path('produtos/', views.produtos, name='produtos'),
    path('carrinhos/', views.carrinhos, name='carrinhos'),
    path('carrinho/<int:carrinho_id>/', views.carrinho_detail, name='carrinho_detail'),
]
