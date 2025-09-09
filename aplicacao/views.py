from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Cliente, Venda, ItemVenda
from django.http.response import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClienteForm, PerfilForm
from django.utils import timezone
from decimal import Decimal


def index(request):
    return redirect('url_entrar')

@login_required(login_url="url_entrar")
def produto(request):
    produtos = Produto.objects.all()
    context = {
        'produtos': produtos,
    }
    return render(request, 'produto.html', context)

@login_required(login_url="url_entrar")
def cad_produto(request):
    if request.method == "POST":
        nome = request.POST.get('nome')
        preco = request.POST.get('preco', '0').replace(',', '.')
        qtde = request.POST.get('qtde', '0')
        Produto.objects.create(nome=nome, preco=Decimal(preco), qtde=int(qtde))
        messages.success(request, 'Produto cadastrado com sucesso!')
        return redirect('url_produto')
    return render(request, 'cad_produto.html')

@login_required(login_url="url_entrar")
def atualizar_produto(request, id):
    prod = get_object_or_404(Produto, id=id)
    if request.method == "POST":
        prod.nome = request.POST.get('nome')
        prod.preco = Decimal(request.POST.get('preco', '0').replace(',', '.'))
        prod.qtde = int(request.POST.get('qtde', '0'))
        prod.save()
        messages.success(request, 'Produto atualizado com sucesso!')
        return redirect('url_produto')
    context = {'prod': prod}
    return render(request, 'atualizar_produto.html', context)

@login_required(login_url="url_entrar")
def apagar_produto(request, id):
    prod = get_object_or_404(Produto, id=id)
    prod.delete()
    messages.success(request, 'Produto apagado com sucesso!')
    return redirect('url_produto')

def entrar(request):
    if request.method == "POST":
        username = request.POST.get('nome')
        password = request.POST.get('senha')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('url_produto')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, "entrar.html")

def cad_user(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        if User.objects.filter(username=nome).exists():
            messages.error(request, 'Este nome de usuário já existe.')
        else:
            User.objects.create_user(username=nome, email=email, password=senha)
            messages.success(request, 'Usuário cadastrado com sucesso! Faça o login.')
            return redirect('url_entrar')
    return render(request, "cad_user.html")
    
def sair(request):
    logout(request)
    return redirect('url_entrar')

@login_required(login_url="url_entrar")
def cad_cliente(request):
    if request.method == "POST":
        form_cliente = ClienteForm(request.POST)
        form_perfil = PerfilForm(request.POST)
        if form_cliente.is_valid() and form_perfil.is_valid():
            cliente = form_cliente.save()
            perfil = form_perfil.save(commit=False)
            perfil.cliente = cliente
            perfil.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('url_produto')
    else:
        form_cliente = ClienteForm()
        form_perfil = PerfilForm()
    context = {
        'form_cliente': form_cliente,
        'form_perfil': form_perfil
    }
    return render(request, "cad_cliente.html", context)

@login_required(login_url="url_entrar")
def registrar_venda(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        if not cliente_id:
            messages.error(request, 'Você precisa selecionar um cliente.')
            return redirect('url_registrar_venda')

        cliente = get_object_or_404(Cliente, id=cliente_id)

        with transaction.atomic():
            nova_venda = Venda.objects.create(cliente=cliente)
            valor_total_venda = Decimal('0.0')
            pelo_menos_um_produto = False

            for produto in Produto.objects.all():
                quantidade_str = request.POST.get(f'produto_{produto.id}')
                if quantidade_str and int(quantidade_str) > 0:
                    pelo_menos_um_produto = True
                    quantidade = int(quantidade_str)

                    if quantidade > produto.qtde:
                        messages.error(request, f"Erro! Estoque insuficiente para o produto '{produto.nome}'.")
                        transaction.set_rollback(True)
                        return redirect('url_registrar_venda')

                    ItemVenda.objects.create(
                        venda=nova_venda,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.preco
                    )
                    
                    produto.qtde -= quantidade
                    produto.save() 
                    valor_total_venda += produto.preco * quantidade
            
            if not pelo_menos_um_produto:
                messages.error(request, 'A venda precisa ter pelo menos um produto.')
                transaction.set_rollback(True)
                return redirect('url_registrar_venda')
         
            nova_venda.valor_total = valor_total_venda
            nova_venda.save()
            
            messages.success(request, 'Venda registrada com sucesso!')
            return redirect('url_produto')

    else: 
        clientes = Cliente.objects.all()
        produtos = Produto.objects.all()
        context = {
            'clientes': clientes,
            'produtos': produtos,
        }
        return render(request, 'registrar_venda.html', context)

@login_required(login_url="url_entrar")
def lista_vendas(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    context = {
        'vendas': vendas
    }
    return render(request, 'lista_vendas.html', context)