from rest_framework import serializers
import requests
from django.conf import settings
from .models import ApiModel, Basket, BasketItem


class ApiModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiModel
        fields = ['identificador', 'nome']
        read_only_fields = ['identificador']  # Campo auto-incremento é somente leitura


class BasketSerializer(serializers.ModelSerializer):
    total_itens = serializers.SerializerMethodField()
    valor_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Basket
        fields = ['id', 'nome', 'estabelecimento', 'total_itens', 'valor_total', 'data_criacao', 'data_atualizacao']
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']
    
    def get_total_itens(self, obj):
        """Retorna o total de itens únicos no carrinho"""
        return obj.itens.count()
    
    def get_valor_total(self, obj):
        """Calcula o valor total do carrinho"""
        valor_total = 0.0
        base_url = getattr(settings, 'ITEMS_API_URL', 'http://localhost:8000/api/produtos/')
        
        for item in obj.itens.all():
            try:
                response = requests.get(f"{base_url}{item.produto_id}/", timeout=5)
                if response.status_code == 200:
                    produto_data = response.json()
                    preco = float(produto_data.get('preco', 0))
                    valor_total += preco * item.quantidade
            except (requests.RequestException, ValueError, TypeError):
                continue
        
        return round(valor_total, 2)


class BasketItemSerializer(serializers.ModelSerializer):
    produto_nome = serializers.SerializerMethodField()
    produto_preco = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    basket_nome = serializers.SerializerMethodField()
    
    class Meta:
        model = BasketItem
        fields = ['id', 'basket', 'basket_nome', 'produto_id', 'produto_nome', 'produto_preco', 'quantidade', 'subtotal', 'data_adicionado']
        read_only_fields = ['id', 'data_adicionado']
    
    def get_basket_nome(self, obj):
        """Retorna o nome do carrinho"""
        return f"{obj.basket.nome} - {obj.basket.estabelecimento}"
    
    def get_produto_nome(self, obj):
        try:
            base_url = getattr(settings, 'ITEMS_API_URL', 'http://localhost:8000/api/produtos/')
            response = requests.get(f"{base_url}{obj.produto_id}/", timeout=5)
            if response.status_code == 200:
                produto_data = response.json()
                return produto_data.get('nome', 'Produto não encontrado')
            return 'Produto não encontrado'
        except requests.RequestException:
            return 'Erro ao buscar produto'
    
    def get_produto_preco(self, obj):
        """Busca o preço do produto via API do items_app"""
        try:
            base_url = getattr(settings, 'ITEMS_API_URL', 'http://localhost:8000/api/produtos/')
            response = requests.get(f"{base_url}{obj.produto_id}/", timeout=5)
            if response.status_code == 200:
                produto_data = response.json()
                return produto_data.get('preco', '0.00')
            return '0.00'
        except requests.RequestException:
            return '0.00'
    
    def get_subtotal(self, obj):
        try:
            preco_str = self.get_produto_preco(obj)
            preco = float(preco_str) if preco_str != '0.00' and preco_str != 'Erro ao buscar produto' else 0.0
            return round(preco * obj.quantidade, 2)
        except (ValueError, TypeError):
            return 0.0
