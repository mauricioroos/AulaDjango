# aplicacao/urls.py
from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.index, name="url_index"),
    path('produto', views.produto, name="url_produto"),
    path('lista_vendas', views.lista_vendas, name="url_lista_vendas"),
    path('cad_produto', views.cad_produto, name="url_cad_produto"),
    path('atualizar_produto/<int:id>', views.atualizar_produto, name="url_atualizar_produto"),
    path('apagar_produto/<int:id>', views.apagar_produto, name="url_apagar_produto"),
    path('entrar', views.entrar, name="url_entrar"),
    path('cad_user', views.cad_user, name="url_cad_user"),
    path('cad_cliente', views.cad_cliente, name="url_cad_cliente"),
    path('registrar_venda', views.registrar_venda, name="url_registrar_venda"),
    path('sair', views.sair, name="url_sair"),
    path('dashboard/', views.dashboard_view, name='url_dashboard'),
]