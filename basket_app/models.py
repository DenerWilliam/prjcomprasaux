from django.db import models

class ApiModel(models.Model):
    identificador = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Basket(models.Model):
    nome = models.CharField(max_length=200, help_text="Nome da lista de compras")
    estabelecimento = models.CharField(max_length=200, help_text="Nome do estabelecimento")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} - {self.estabelecimento}"


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='itens')
    produto_id = models.IntegerField(help_text="ID do produto no items_app")
    quantidade = models.PositiveIntegerField(default=1)
    data_adicionado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_adicionado']
    
    def __str__(self):
        return f"{self.basket.nome} - Produto ID: {self.produto_id} - Qtd: {self.quantidade}"