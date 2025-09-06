from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, Mock
from .models import Basket, BasketItem, ApiModel
from .serializers import ApiModelSerializer, BasketSerializer, BasketItemSerializer


class BasketModelTest(TestCase):
    def setUp(self):
        self.basket = Basket.objects.create(
            nome="Lista Teste",
            estabelecimento="Supermercado Teste"
        )
    
    def test_basket_creation(self):
        """Testa a criação de um carrinho"""
        self.assertEqual(self.basket.nome, "Lista Teste")
        self.assertEqual(self.basket.estabelecimento, "Supermercado Teste")
        self.assertTrue(isinstance(self.basket, Basket))
    
    def test_basket_str_representation(self):
        """Testa a representação string do carrinho"""
        expected_str = "Lista Teste - Supermercado Teste"
        self.assertEqual(str(self.basket), expected_str)
    
    def test_basket_fields(self):
        """Testa se todos os campos estão presentes"""
        self.assertIsNotNone(self.basket.id)
        self.assertIsNotNone(self.basket.nome)
        self.assertIsNotNone(self.basket.estabelecimento)
        self.assertIsNotNone(self.basket.data_criacao)
        self.assertIsNotNone(self.basket.data_atualizacao)


class BasketItemModelTest(TestCase):
    """Testes para o modelo BasketItem"""
    
    def setUp(self):
        self.basket = Basket.objects.create(
            nome="Lista Teste",
            estabelecimento="Supermercado Teste"
        )
        self.basket_item = BasketItem.objects.create(
            basket=self.basket,
            produto_id=1,
            quantidade=2
        )
    
    def test_basket_item_creation(self):
        """Testa a criação de um item do carrinho"""
        self.assertEqual(self.basket_item.basket, self.basket)
        self.assertEqual(self.basket_item.produto_id, 1)
        self.assertEqual(self.basket_item.quantidade, 2)
        self.assertTrue(isinstance(self.basket_item, BasketItem))
    
    def test_basket_item_str_representation(self):
        """Testa a representação string do item"""
        expected_str = "Lista Teste - Produto ID: 1 - Qtd: 2"
        self.assertEqual(str(self.basket_item), expected_str)
    
    def test_basket_item_default_quantity(self):
        """Testa se a quantidade padrão é 1"""
        item = BasketItem.objects.create(
            basket=self.basket,
            produto_id=2
        )
        self.assertEqual(item.quantidade, 1)
    
    def test_basket_item_cascade_delete(self):
        """Testa se os itens são deletados quando o carrinho é deletado"""
        basket_id = self.basket.id
        self.basket.delete()
        self.assertFalse(BasketItem.objects.filter(basket_id=basket_id).exists())


class BasketAPITest(APITestCase):
    """Testes para a API de Carrinhos"""
    
    def setUp(self):
        self.basket_data = {
            'nome': 'Lista API Teste',
            'estabelecimento': 'Supermercado API'
        }
        self.basket = Basket.objects.create(
            nome="Lista Existente",
            estabelecimento="Supermercado Existente"
        )
    
    def test_create_basket(self):
        """Testa a criação de um carrinho via API"""
        url = reverse('basketlist-list')
        response = self.client.post(url, self.basket_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Basket.objects.count(), 2)
        self.assertEqual(Basket.objects.get(id=2).nome, 'Lista API Teste')
    
    def test_list_baskets(self):
        """Testa a listagem de carrinhos via API"""
        url = reverse('basketlist-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Lista Existente')
    
    def test_retrieve_basket(self):
        """Testa a busca de um carrinho específico via API"""
        url = reverse('basketlist-detail', kwargs={'pk': self.basket.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Lista Existente')
        self.assertEqual(response.data['estabelecimento'], 'Supermercado Existente')
    
    def test_update_basket(self):
        """Testa a atualização de um carrinho via API"""
        url = reverse('basketlist-detail', kwargs={'pk': self.basket.id})
        update_data = {'nome': 'Lista Atualizada', 'estabelecimento': 'Supermercado Atualizado'}
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.basket.refresh_from_db()
        self.assertEqual(self.basket.nome, 'Lista Atualizada')
        self.assertEqual(self.basket.estabelecimento, 'Supermercado Atualizado')
    
    def test_delete_basket(self):
        """Testa a exclusão de um carrinho via API"""
        url = reverse('basketlist-detail', kwargs={'pk': self.basket.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Basket.objects.count(), 0)


class BasketItemAPITest(APITestCase):
    """Testes para a API de Itens do Carrinho"""
    
    def setUp(self):
        self.basket = Basket.objects.create(
            nome="Lista Teste",
            estabelecimento="Supermercado Teste"
        )
        self.basket_item_data = {
            'basket': self.basket.id,
            'produto_id': 1,
            'quantidade': 2
        }
        self.basket_item = BasketItem.objects.create(
            basket=self.basket,
            produto_id=1,
            quantidade=1
        )
    
    @patch('requests.get')
    def test_create_basket_item(self, mock_get):
        """Testa a criação de um item do carrinho via API"""
        # Mock da resposta da API de produtos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '29.99'}
        mock_get.return_value = mock_response
        
        url = reverse('basketitem-list')
        response = self.client.post(url, self.basket_item_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BasketItem.objects.count(), 2)
        self.assertEqual(BasketItem.objects.get(id=2).produto_id, 1)
    
    @patch('requests.get')
    def test_list_basket_items(self, mock_get):
        """Testa a listagem de itens do carrinho via API"""
        # Mock da resposta da API de produtos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '29.99'}
        mock_get.return_value = mock_response
        
        url = reverse('basketitem-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['produto_id'], 1)
    
    @patch('requests.get')
    def test_retrieve_basket_item(self, mock_get):
        """Testa a busca de um item específico via API"""
        # Mock da resposta da API de produtos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '29.99'}
        mock_get.return_value = mock_response
        
        url = reverse('basketitem-detail', kwargs={'pk': self.basket_item.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['produto_id'], 1)
        self.assertEqual(response.data['quantidade'], 1)
    
    def test_update_basket_item(self):
        """Testa a atualização de um item via API"""
        url = reverse('basketitem-detail', kwargs={'pk': self.basket_item.id})
        update_data = {'basket': self.basket.id, 'produto_id': 1, 'quantidade': 3}
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.basket_item.refresh_from_db()
        self.assertEqual(self.basket_item.quantidade, 3)
    
    def test_delete_basket_item(self):
        """Testa a exclusão de um item via API"""
        url = reverse('basketitem-detail', kwargs={'pk': self.basket_item.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BasketItem.objects.count(), 0)


class BasketSummaryAPITest(APITestCase):
    """Testes para a API de Resumo do Carrinho"""
    
    def setUp(self):
        self.basket = Basket.objects.create(
            nome="Lista Teste",
            estabelecimento="Supermercado Teste"
        )
        self.basket_item = BasketItem.objects.create(
            basket=self.basket,
            produto_id=1,
            quantidade=2
        )
    
    @patch('requests.get')
    def test_basket_summary_general(self, mock_get):
        """Testa o resumo geral de todos os carrinhos"""
        # Mock da resposta da API de produtos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '29.99'}
        mock_get.return_value = mock_response
        
        url = reverse('basket-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_itens_unicos'], 1)
        self.assertEqual(response.data['total_quantidade'], 2)
        self.assertEqual(response.data['valor_total'], 59.98)
    
    @patch('requests.get')
    def test_basket_summary_specific(self, mock_get):
        """Testa o resumo de um carrinho específico"""
        # Mock da resposta da API de produtos
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '29.99'}
        mock_get.return_value = mock_response
        
        url = reverse('basket-summary-specific', kwargs={'basket_id': self.basket.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_itens_unicos'], 1)
        self.assertEqual(response.data['total_quantidade'], 2)
        self.assertEqual(response.data['valor_total'], 59.98)
        self.assertIn('basket_info', response.data)
        self.assertEqual(response.data['basket_info']['basket_nome'], 'Lista Teste')
    
    def test_basket_summary_not_found(self):
        """Testa resumo de carrinho inexistente"""
        url = reverse('basket-summary-specific', kwargs={'basket_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    @patch('basket_app.views.requests.get')
    def test_basket_summary_api_error(self, mock_get):
        """Testa resumo quando há erro na API de produtos"""
        # Mock de erro na API
        mock_get.side_effect = Exception("API Error")
        
        url = reverse('basket-summary')
        response = self.client.get(url)
        
        # Quando há erro na API, o endpoint retorna 500 com mensagem de erro
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('erro', response.data)
        self.assertIn('API Error', response.data['erro'])


class ApiModelTest(TestCase):
    def setUp(self):
        self.api_model = ApiModel.objects.create(
            nome="Modelo Teste"
        )
    
    def test_api_model_creation(self):
        """Testa a criação de um ApiModel"""
        self.assertEqual(self.api_model.nome, "Modelo Teste")
        self.assertTrue(isinstance(self.api_model, ApiModel))
    
    def test_api_model_str_representation(self):
        """Testa a representação string do ApiModel"""
        self.assertEqual(str(self.api_model), "Modelo Teste")


class SerializerTest(TestCase):
    """Testes específicos para os serializers"""
    
    def setUp(self):
        self.basket = Basket.objects.create(
            nome="Lista Serializer Teste",
            estabelecimento="Supermercado Serializer"
        )
        self.basket_item = BasketItem.objects.create(
            basket=self.basket,
            produto_id=1,
            quantidade=3
        )
        self.api_model = ApiModel.objects.create(
            nome="Modelo Serializer Teste"
        )
    
    def test_api_model_serializer(self):
        """Testa o ApiModelSerializer"""
        serializer = ApiModelSerializer(self.api_model)
        data = serializer.data
        
        self.assertEqual(data['identificador'], self.api_model.identificador)
        self.assertEqual(data['nome'], 'Modelo Serializer Teste')
        self.assertIn('identificador', data)
        self.assertIn('nome', data)
    
    def test_basket_serializer_fields(self):
        """Testa os campos do BasketSerializer"""
        serializer = BasketSerializer(self.basket)
        data = serializer.data
        
        expected_fields = ['id', 'nome', 'estabelecimento', 'total_itens', 'valor_total', 'data_criacao', 'data_atualizacao']
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['nome'], 'Lista Serializer Teste')
        self.assertEqual(data['estabelecimento'], 'Supermercado Serializer')
    
    def test_basket_serializer_total_itens(self):
        """Testa o método get_total_itens do BasketSerializer"""
        serializer = BasketSerializer(self.basket)
        total_itens = serializer.get_total_itens(self.basket)
        
        self.assertEqual(total_itens, 1)  # 1 item no carrinho
        
        # Adicionar mais um item
        BasketItem.objects.create(basket=self.basket, produto_id=2, quantidade=1)
        total_itens = serializer.get_total_itens(self.basket)
        self.assertEqual(total_itens, 2)  # 2 itens no carrinho
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_serializer_valor_total_success(self, mock_get):
        """Testa o método get_valor_total com sucesso na API"""
        # Mock da resposta da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '15.50'}
        mock_get.return_value = mock_response
        
        serializer = BasketSerializer(self.basket)
        valor_total = serializer.get_valor_total(self.basket)
        
        # 3 itens * R$ 15,50 = R$ 46,50
        self.assertEqual(valor_total, 46.50)
        mock_get.assert_called_once()
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_serializer_valor_total_api_error(self, mock_get):
        """Testa o método get_valor_total com erro na API"""
        # Mock de erro na API
        mock_get.side_effect = Exception("API Error")
        
        serializer = BasketSerializer(self.basket)
        valor_total = serializer.get_valor_total(self.basket)
        
        # Deve retornar 0.0 quando há erro
        self.assertEqual(valor_total, 0.0)
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_serializer_valor_total_invalid_response(self, mock_get):
        """Testa o método get_valor_total com resposta inválida"""
        # Mock de resposta inválida
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste'}  # Sem preço
        mock_get.return_value = mock_response
        
        serializer = BasketSerializer(self.basket)
        valor_total = serializer.get_valor_total(self.basket)
        
        # Deve retornar 0.0 quando não há preço
        self.assertEqual(valor_total, 0.0)
    
    def test_basket_item_serializer_fields(self):
        """Testa os campos do BasketItemSerializer"""
        serializer = BasketItemSerializer(self.basket_item)
        data = serializer.data
        
        expected_fields = ['id', 'basket', 'basket_nome', 'produto_id', 'produto_nome', 'produto_preco', 'quantidade', 'subtotal', 'data_adicionado']
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['produto_id'], 1)
        self.assertEqual(data['quantidade'], 3)
    
    def test_basket_item_serializer_basket_nome(self):
        """Testa o método get_basket_nome do BasketItemSerializer"""
        serializer = BasketItemSerializer(self.basket_item)
        basket_nome = serializer.get_basket_nome(self.basket_item)
        
        expected_nome = "Lista Serializer Teste - Supermercado Serializer"
        self.assertEqual(basket_nome, expected_nome)
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_nome_success(self, mock_get):
        """Testa o método get_produto_nome com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '15.50'}
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_nome = serializer.get_produto_nome(self.basket_item)
        
        self.assertEqual(produto_nome, 'Produto Teste')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_nome_not_found(self, mock_get):
        """Testa o método get_produto_nome quando produto não é encontrado"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_nome = serializer.get_produto_nome(self.basket_item)
        
        self.assertEqual(produto_nome, 'Produto não encontrado')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_nome_api_error(self, mock_get):
        """Testa o método get_produto_nome com erro na API"""
        mock_get.side_effect = Exception("API Error")
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_nome = serializer.get_produto_nome(self.basket_item)
        
        self.assertEqual(produto_nome, 'Erro ao buscar produto')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_preco_success(self, mock_get):
        """Testa o método get_produto_preco com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '15.50'}
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_preco = serializer.get_produto_preco(self.basket_item)
        
        self.assertEqual(produto_preco, '15.50')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_preco_not_found(self, mock_get):
        """Testa o método get_produto_preco quando produto não é encontrado"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_preco = serializer.get_produto_preco(self.basket_item)
        
        self.assertEqual(produto_preco, '0.00')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_produto_preco_api_error(self, mock_get):
        """Testa o método get_produto_preco com erro na API"""
        mock_get.side_effect = Exception("API Error")
        
        serializer = BasketItemSerializer(self.basket_item)
        produto_preco = serializer.get_produto_preco(self.basket_item)
        
        self.assertEqual(produto_preco, '0.00')
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_subtotal_success(self, mock_get):
        """Testa o método get_subtotal com sucesso"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '15.50'}
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        subtotal = serializer.get_subtotal(self.basket_item)
        
        # 3 itens * R$ 15,50 = R$ 46,50
        self.assertEqual(subtotal, 46.50)
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_subtotal_invalid_preco(self, mock_get):
        """Testa o método get_subtotal com preço inválido"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': '0.00'}
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        subtotal = serializer.get_subtotal(self.basket_item)
        
        # Deve retornar 0.0 quando preço é inválido
        self.assertEqual(subtotal, 0.0)
    
    @patch('basket_app.serializers.requests.get')
    def test_basket_item_serializer_subtotal_error_preco(self, mock_get):
        """Testa o método get_subtotal quando get_produto_preco retorna erro"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'nome': 'Produto Teste', 'preco': 'Erro ao buscar produto'}
        mock_get.return_value = mock_response
        
        serializer = BasketItemSerializer(self.basket_item)
        subtotal = serializer.get_subtotal(self.basket_item)
        
        # Deve retornar 0.0 quando há erro
        self.assertEqual(subtotal, 0.0)
