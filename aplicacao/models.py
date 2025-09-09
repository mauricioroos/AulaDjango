from django.db import models
from django.utils import timezone 
class Produto(models.Model):
    nome = models.CharField("Nome", max_length=200, null = True)
    preco = models.DecimalField("Preço", decimal_places=2, max_digits=8, null = True)
    qtde = models.PositiveIntegerField("Quantidade", default=0, null = True)
    def __str__(self):
        return self.nome
    
class Cliente(models.Model):
    nome = models.CharField("Nome", max_length=200)
    email = models.EmailField("Email", unique=True)
    def __str__(self):
        return self.nome
    
class Perfil(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='perfil')
    telefone = models.CharField("Telefone", max_length=20)
    rua = models.CharField("Rua", max_length=200)
    numero = models.PositiveIntegerField("Nº")
    cep = models.CharField("CEP", max_length=20)
    bairro = models.CharField("Bairro", max_length=50)
    cidade = models.CharField("Cidade", max_length=50)
    complemento = models.CharField("Complemento", max_length=200)
    def __str__(self):

        return f'{self.rua}, {self.numero} - {self.bairro}'

class Venda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(default=timezone.now)
    valor_total = models.DecimalField("Valor Total", max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Venda {self.id} - {self.cliente.nome}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField("Quantidade")
    preco_unitario = models.DecimalField("Preço Unitário", max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome}"
