from rest_framework import serializers
from .models import Produto


class ProdutoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Produto.
    Permite serialização e deserialização dos dados de produtos.
    """
    
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco']
        read_only_fields = ['id']  # Campo auto-incremento é somente leitura
