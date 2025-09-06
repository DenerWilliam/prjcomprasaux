"""
Testes de Integração entre os módulos items_app e basket_app
"""
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
import requests
from items_app.models import Produto
from basket_app.models import Basket, BasketItem


class IntegrationTest(TransactionTestCase):
    """Testes de integração entre os módulos"""
    
    def setUp(self):
        # Criar produtos no items_app
        self.produto1 = Produto.objects.create(
            nome="Arroz",
            preco=5.99
        )
        self.produto2 = Produto.objects.create(
            nome="Feijão",
            preco=4.50
        )
        
        # Criar carrinho no basket_app
        self.basket = Basket.objects.create(
            nome="Compras do mês",
            estabelecimento="Supermercado ABC"
        )
    
    @patch('basket_app.serializers.requests.get')
    def test_full_integration_flow(self, mock_get):
        """Testa o fluxo completo de integração entre os módulos"""
        
        # Mock das respostas da API de produtos
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            if str(self.produto1.id) in url:
                mock_response.json.return_value = {'nome': 'Arroz', 'preco': '5.99'}
            elif str(self.produto2.id) in url:
                mock_response.json.return_value = {'nome': 'Feijão', 'preco': '4.50'}
            else:
                mock_response.json.return_value = {'nome': 'Produto não encontrado', 'preco': '0.00'}
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # 1. Criar itens no carrinho referenciando produtos do items_app
        item1 = BasketItem.objects.create(
            basket=self.basket,
            produto_id=self.produto1.id,
            quantidade=2
        )
        
        item2 = BasketItem.objects.create(
            basket=self.basket,
            produto_id=self.produto2.id,
            quantidade=3
        )
        
        # 2. Verificar se os itens foram criados corretamente
        self.assertEqual(BasketItem.objects.count(), 2)
        self.assertEqual(item1.produto_id, self.produto1.id)
        self.assertEqual(item2.produto_id, self.produto2.id)
        
        # 3. Verificar se o carrinho tem os itens corretos
        self.assertEqual(self.basket.itens.count(), 2)
        
        # 4. Testar serialização com dados da API
        from basket_app.serializers import BasketItemSerializer
        
        serializer = BasketItemSerializer(item1)
        data = serializer.data
        
        self.assertEqual(data['produto_id'], self.produto1.id)
        self.assertEqual(data['produto_nome'], 'Arroz')
        self.assertEqual(data['produto_preco'], '5.99')
        self.assertEqual(data['quantidade'], 2)
        self.assertEqual(data['subtotal'], 11.98)  # 5.99 * 2
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_total_calculation(self, mock_get):
        """Testa o cálculo do total do carrinho com integração"""
        
        # Mock das respostas da API
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            if str(self.produto1.id) in url:
                mock_response.json.return_value = {'nome': 'Arroz', 'preco': '5.99'}
            elif str(self.produto2.id) in url:
                mock_response.json.return_value = {'nome': 'Feijão', 'preco': '4.50'}
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Criar itens
        BasketItem.objects.create(
            basket=self.basket,
            produto_id=self.produto1.id,
            quantidade=2
        )
        
        BasketItem.objects.create(
            basket=self.basket,
            produto_id=self.produto2.id,
            quantidade=1
        )
        
        # Testar serializer do Basket
        from basket_app.serializers import BasketSerializer
        
        serializer = BasketSerializer(self.basket)
        data = serializer.data
        
        # Verificar cálculos
        self.assertEqual(data['total_itens'], 2)
        self.assertEqual(data['valor_total'], 16.48)  # (5.99 * 2) + (4.50 * 1)
    
    def test_api_error_handling(self):
        """Testa o tratamento de erros da API"""
        
        # Mock de erro na API
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")
            
            # Criar item mesmo com erro na API
            item = BasketItem.objects.create(
                basket=self.basket,
                produto_id=999,  # Produto inexistente
                quantidade=1
            )
            
            # Testar serializer com erro
            from basket_app.serializers import BasketItemSerializer
            
            serializer = BasketItemSerializer(item)
            data = serializer.data
            
            # Verificar tratamento de erro
            self.assertEqual(data['produto_nome'], 'Erro ao buscar produto')
            self.assertEqual(data['produto_preco'], '0.00')
            self.assertEqual(data['subtotal'], 0.0)


class APIIntegrationTest(APITestCase):
    """Testes de integração via API"""
    
    def setUp(self):
        # Criar produtos
        self.produto1 = Produto.objects.create(nome="Arroz", preco=5.99)
        self.produto2 = Produto.objects.create(nome="Feijão", preco=4.50)
        
        # Criar carrinho
        self.basket = Basket.objects.create(
            nome="Compras do mês",
            estabelecimento="Supermercado ABC"
        )
    
    @patch('requests.get')
    def test_api_integration_flow(self, mock_get):
        """Testa o fluxo completo via API"""
        
        # Mock das respostas da API
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            if '1' in url:
                mock_response.json.return_value = {'nome': 'Arroz', 'preco': '5.99'}
            elif '2' in url:
                mock_response.json.return_value = {'nome': 'Feijão', 'preco': '4.50'}
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # 1. Criar item via API
        item_data = {
            'basket': self.basket.id,
            'produto_id': self.produto1.id,
            'quantidade': 2
        }
        
        url = reverse('basketitem-list')
        response = self.client.post(url, item_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['produto_nome'], 'Arroz')
        self.assertEqual(response.data['subtotal'], 11.98)
        
        # 2. Buscar resumo do carrinho
        url = reverse('basket-summary-specific', kwargs={'basket_id': self.basket.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_itens_unicos'], 1)
        self.assertEqual(response.data['valor_total'], 11.98)
    
    @patch('basket_app.views.requests.get')
    def test_multiple_baskets_integration(self, mock_get):
        """Testa integração com múltiplos carrinhos"""
        
        # Mock das respostas da API
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            if str(self.produto1.id) in url:
                mock_response.json.return_value = {'nome': 'Arroz', 'preco': '5.99'}
            elif str(self.produto2.id) in url:
                mock_response.json.return_value = {'nome': 'Feijão', 'preco': '4.50'}
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Criar segundo carrinho
        basket2 = Basket.objects.create(
            nome="Compras da farmácia",
            estabelecimento="Farmácia XYZ"
        )
        
        # Adicionar itens aos dois carrinhos
        BasketItem.objects.create(
            basket=self.basket,
            produto_id=self.produto1.id,
            quantidade=1
        )
        
        BasketItem.objects.create(
            basket=basket2,
            produto_id=self.produto2.id,
            quantidade=2
        )
        
        # Testar resumo geral
        url = reverse('basket-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_itens_unicos'], 2)
        self.assertEqual(response.data['total_quantidade'], 3)
        self.assertEqual(response.data['valor_total'], 14.99)  # 5.99 + (4.50 * 2) = 5.99 + 9.00 = 14.99
        
        # Verificar se os itens mostram informações dos carrinhos
        items = response.data['itens']
        basket_names = [item['basket_nome'] for item in items]
        
        self.assertIn('Compras do mês - Supermercado ABC', basket_names)
        self.assertIn('Compras da farmácia - Farmácia XYZ', basket_names)


class PerformanceIntegrationTest(TestCase):
    """Testes de performance da integração"""
    
    def setUp(self):
        # Criar muitos produtos
        self.produtos = []
        for i in range(10):
            produto = Produto.objects.create(
                nome=f"Produto {i}",
                preco=10.00 + i
            )
            self.produtos.append(produto)
        
        # Criar carrinho
        self.basket = Basket.objects.create(
            nome="Lista Grande",
            estabelecimento="Supermercado Grande"
        )
    
    @patch('basket_app.serializers.requests.get')
    def test_large_basket_performance(self, mock_get):
        """Testa performance com carrinho grande"""
        
        # Mock das respostas da API
        def mock_get_side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            
            # Extrair ID do produto da URL
            produto_id = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            produto = Produto.objects.get(id=produto_id)
            
            mock_response.json.return_value = {
                'nome': produto.nome,
                'preco': str(produto.preco)
            }
            
            return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # Criar muitos itens
        for produto in self.produtos:
            BasketItem.objects.create(
                basket=self.basket,
                produto_id=produto.id,
                quantidade=2
            )
        
        # Testar serialização
        from basket_app.serializers import BasketSerializer
        
        serializer = BasketSerializer(self.basket)
        data = serializer.data
        
        # Verificar se todos os itens foram processados
        self.assertEqual(data['total_itens'], 10)
        self.assertGreater(data['valor_total'], 0)
        
        # Verificar se todas as chamadas da API foram feitas
        self.assertEqual(mock_get.call_count, 10)
