from django.contrib import admin
from .models import Produto, Cliente, Perfil
from .models import Venda, ItemVenda

class ProdutoAdm(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'qtde')

admin.site.register(Produto, ProdutoAdm)
admin.site.register(Cliente)
admin.site.register(Venda)
admin.site.register(ItemVenda)

