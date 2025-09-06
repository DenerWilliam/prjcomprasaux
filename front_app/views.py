from django.shortcuts import render


def home(request):
    """
    Página principal do sistema de compras
    """
    return render(request, 'front_app/home.html')


def produtos(request):
    """
    Página de listagem de produtos
    """
    return render(request, 'front_app/produtos.html')


def carrinhos(request):
    """
    Página de listagem de carrinhos
    """
    return render(request, 'front_app/carrinhos.html')


def carrinho_detail(request, carrinho_id):
    """
    Página de detalhes de um carrinho específico
    """
    return render(request, 'front_app/carrinho_detail.html', {'carrinho_id': carrinho_id})