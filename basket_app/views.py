from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count
import requests
from django.conf import settings
from .models import ApiModel, Basket, BasketItem
from .serializers import ApiModelSerializer, BasketSerializer, BasketItemSerializer

class ApiModelViewSet(viewsets.ModelViewSet):
    queryset = ApiModel.objects.all()
    serializer_class = ApiModelSerializer

class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

class BasketItemViewSet(viewsets.ModelViewSet):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemSerializer

@api_view(['GET'])
def basket_summary(request, basket_id=None):
    """
    Endpoint que retorna o resumo do carrinho:
    - Se basket_id for fornecido, retorna resumo de um carrinho específico
    - Se não, retorna resumo de todos os carrinhos
    """
    try:
        if basket_id:
            # Resumo de um carrinho específico
            try:
                basket = Basket.objects.get(id=basket_id)
                basket_items = basket.itens.all()
                basket_info = {
                    'basket_id': basket.id,
                    'basket_nome': basket.nome,
                    'estabelecimento': basket.estabelecimento,
                    'data_criacao': basket.data_criacao
                }
            except Basket.DoesNotExist:
                return Response(
                    {'erro': f'Carrinho com ID {basket_id} não encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Resumo de todos os carrinhos
            basket_items = BasketItem.objects.all()
            basket_info = None

        # Calcular totais
        total_itens_unicos = basket_items.count()
        total_quantidade = basket_items.aggregate(total=Sum('quantidade'))['total'] or 0

        # Calcular valor total
        valor_total = 0.0
        base_url = getattr(settings, 'ITEMS_API_URL', 'http://localhost:8000/api/produtos/')

        for item in basket_items:
            try:
                # Buscar preço do produto via API
                response = requests.get(f"{base_url}{item.produto_id}/", timeout=5)
                if response.status_code == 200:
                    produto_data = response.json()
                    preco = float(produto_data.get('preco', 0))
                    valor_total += preco * item.quantidade
            except (requests.RequestException, ValueError, TypeError):
                continue

        # Preparar resposta
        summary = {
            'total_itens_unicos': total_itens_unicos,
            'total_quantidade': total_quantidade,
            'valor_total': round(valor_total, 2),
            'itens': []
        }

        # Adicionar informações do carrinho se for específico
        if basket_info:
            summary['basket_info'] = basket_info

        # Adicionar detalhes dos itens
        for item in basket_items:
            try:
                response = requests.get(f"{base_url}{item.produto_id}/", timeout=5)
                if response.status_code == 200:
                    produto_data = response.json()
                    preco = float(produto_data.get('preco', 0))
                    subtotal = preco * item.quantidade

                    item_data = {
                        'produto_id': item.produto_id,
                        'produto_nome': produto_data.get('nome', 'Produto não encontrado'),
                        'quantidade': item.quantidade,
                        'preco_unitario': preco,
                        'subtotal': round(subtotal, 2)
                    }

                    if not basket_id:
                        item_data['basket_id'] = item.basket.id
                        item_data['basket_nome'] = f"{item.basket.nome} - {item.basket.estabelecimento}"

                    summary['itens'].append(item_data)
            except (requests.RequestException, ValueError, TypeError):
                item_data = {
                    'produto_id': item.produto_id,
                    'produto_nome': 'Erro ao buscar produto',
                    'quantidade': item.quantidade,
                    'preco_unitario': 0.0,
                    'subtotal': 0.0
                }

                if not basket_id:
                    item_data['basket_id'] = item.basket.id
                    item_data['basket_nome'] = f"{item.basket.nome} - {item.basket.estabelecimento}"

                summary['itens'].append(item_data)

        return Response(summary, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'erro': f'Erro ao calcular resumo do carrinho: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

