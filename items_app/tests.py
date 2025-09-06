from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Produto


class ProdutoModelTest(TestCase):
    def setUp(self):
        self.produto = Produto.objects.create(
            nome="Produto Teste",
            preco=29.99
        )
    
    def test_produto_creation(self):
        """Testa a criação de um produto"""
        self.assertEqual(self.produto.nome, "Produto Teste")
        self.assertEqual(self.produto.preco, 29.99)
        self.assertTrue(isinstance(self.produto, Produto))
    
    def test_produto_str_representation(self):
        """Testa a representação string do produto"""
        expected_str = "Produto Teste - R$ 29.99"
        self.assertEqual(str(self.produto), expected_str)
    
    def test_produto_fields(self):
        """Testa se todos os campos estão presentes"""
        self.assertIsNotNone(self.produto.id)
        self.assertIsNotNone(self.produto.nome)
        self.assertIsNotNone(self.produto.preco)


class ProdutoAPITest(APITestCase):
    """Testes para a API de Produtos"""
    
    def setUp(self):
        self.produto_data = {
            'nome': 'Produto API Teste',
            'preco': '19.99'
        }
        self.produto = Produto.objects.create(
            nome="Produto Existente",
            preco=15.50
        )
    
    def test_create_produto(self):
        """Testa a criação de um produto via API"""
        url = reverse('produto-list')
        response = self.client.post(url, self.produto_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produto.objects.count(), 2)
        self.assertEqual(Produto.objects.get(id=2).nome, 'Produto API Teste')
    
    def test_list_produtos(self):
        """Testa a listagem de produtos via API"""
        url = reverse('produto-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Produto Existente')
    
    def test_retrieve_produto(self):
        """Testa a busca de um produto específico via API"""
        url = reverse('produto-detail', kwargs={'pk': self.produto.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], 'Produto Existente')
        self.assertEqual(response.data['preco'], '15.50')
    
    def test_update_produto(self):
        """Testa a atualização de um produto via API"""
        url = reverse('produto-detail', kwargs={'pk': self.produto.id})
        update_data = {'nome': 'Produto Atualizado', 'preco': '25.99'}
        response = self.client.put(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.nome, 'Produto Atualizado')
        self.assertEqual(float(self.produto.preco), 25.99)
    
    def test_partial_update_produto(self):
        """Testa a atualização parcial de um produto via API"""
        url = reverse('produto-detail', kwargs={'pk': self.produto.id})
        update_data = {'preco': '30.00'}
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.preco, 30.00)
        self.assertEqual(self.produto.nome, 'Produto Existente')  # Não deve mudar
    
    def test_delete_produto(self):
        """Testa a exclusão de um produto via API"""
        url = reverse('produto-detail', kwargs={'pk': self.produto.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Produto.objects.count(), 0)
    
    def test_create_produto_invalid_data(self):
        """Testa a criação de produto com dados inválidos"""
        url = reverse('produto-list')
        invalid_data = {'nome': '', 'preco': 'invalid'}
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_produto_not_found(self):
        """Testa busca de produto inexistente"""
        url = reverse('produto-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
