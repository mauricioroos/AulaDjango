# aplicacao/views.py

import matplotlib
matplotlib.use('Agg')
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
import io, pandas as pd, matplotlib.pyplot as plt, urllib, base64
from .models import Produto, Cliente, Venda, ItemVenda, Avaliacao
from .forms import ClienteForm, PerfilForm

# --- FUNÇÕES AUXILIARES PARA AS ANÁLISES ---
def get_dataframe():
    return pd.DataFrame(list(Avaliacao.objects.all().values()))

def plot_to_base_64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    return urllib.parse.quote(base64.b64encode(buf.read()))

# --- SUAS VIEWS ANTIGAS (LOGIN, PRODUTOS, VENDAS, ETC.) ---
def index(request):
    return redirect('url_entrar')

@login_required(login_url="url_entrar")
def produto(request):
    produtos = Produto.objects.all()
    context = {'produtos': produtos}
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
    context = {'form_cliente': form_cliente, 'form_perfil': form_perfil}
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
                    ItemVenda.objects.create(venda=nova_venda, produto=produto, quantidade=quantidade, preco_unitario=produto.preco)
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
        context = {'clientes': clientes, 'produtos': produtos}
        return render(request, 'registrar_venda.html', context)

@login_required(login_url="url_entrar")
def lista_vendas(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    context = {'vendas': vendas}
    return render(request, 'lista_vendas.html', context)

def dashboard_view(request):
    df = get_dataframe()
    
 
    df_filtrado_usr = df.dropna(subset=['profile_name'])
    df_filtrado_usr = df_filtrado_usr[df_filtrado_usr['profile_name'] != 'nan']
    usuarios_ativos = df_filtrado_usr['profile_name'].value_counts().nlargest(15)
    plt.figure(figsize=(10, 8))
    usuarios_ativos.sort_values().plot(kind='barh', color='skyblue')
    plt.title('Top 15 Usuários Mais Ativos'); plt.xlabel('Número de Avaliações'); plt.ylabel('Usuário'); plt.tight_layout()
    grafico_usuarios_ativos = plot_to_base_64(plt.gcf())
    plt.close()

    df_evolucao = df.copy()
    df_evolucao['data_review'] = pd.to_datetime(df_evolucao['review_time'], unit='s')
    df_evolucao['ano'] = df_evolucao['data_review'].dt.year
    avaliacoes_por_ano = df_evolucao['ano'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    avaliacoes_por_ano.plot(kind='line', marker='o', color='red')
    plt.title('Evolução do Nº de Avaliações por Ano'); plt.xlabel('Ano'); plt.ylabel('Qtd de Avaliações'); plt.grid(True); plt.tight_layout()
    grafico_evolucao_reviews = plot_to_base_64(plt.gcf())
    plt.close()

    df_preco = df[(df['price'] > 0) & (df['price'] < 100)]
    plt.figure(figsize=(10, 6))
    plt.scatter(df_preco['price'], df_preco['review_score'], alpha=0.3, color='orange')
    plt.title('Correlação entre Preço e Nota'); plt.xlabel('Preço (USD)'); plt.ylabel('Nota (Score)'); plt.grid(True); plt.tight_layout()
    grafico_preco_score = plot_to_base_64(plt.gcf())
    plt.close()

    positivas = ['good', 'great', 'excellent', 'love', 'recommend']
    negativas = ['bad', 'terrible', 'disappointing', 'not good']
    def classificar(texto):
        texto = str(texto).lower()
        if any(p in texto for p in positivas): return 'Positivo'
        if any(p in texto for p in negativas): return 'Negativo'
        return 'Neutro'
    df['sentimento'] = df['review_summary'].fillna('').apply(classificar)
    contagem = df['sentimento'].value_counts()
    plt.figure(figsize=(8, 8))
    contagem.plot(kind='pie', autopct='%1.1f%%', colors=['lightgreen', 'lightcoral', 'lightskyblue'])
    plt.title('Distribuição de Sentimentos'); plt.ylabel(''); plt.tight_layout()
    grafico_sentimento = plot_to_base_64(plt.gcf())
    plt.close()
    
    plt.figure(figsize=(10, 6))
    df['review_score'].value_counts().sort_index().plot(kind='bar', color='coral')
    plt.title('Distribuição das Notas'); plt.xlabel('Nota'); plt.ylabel('Qtd de Avaliações'); plt.grid(axis='y'); plt.tight_layout()
    grafico_distribuicao_notas = plot_to_base_64(plt.gcf())
    plt.close()


    top_10_livros = df['title'].value_counts().nlargest(10)
    plt.figure(figsize=(10, 8))
    top_10_livros.sort_values().plot(kind='barh', color='teal')
    plt.title('Top 10 Livros Mais Avaliados'); plt.xlabel('Nº de Avaliações'); plt.ylabel('Título do Livro'); plt.tight_layout()
    grafico_top_livros = plot_to_base_64(plt.gcf())
    plt.close()

    context = {
        'grafico_usuarios_ativos': grafico_usuarios_ativos,
        'grafico_evolucao_reviews': grafico_evolucao_reviews,
        'grafico_preco_score': grafico_preco_score,
        'grafico_sentimento': grafico_sentimento,
        'grafico_distribuicao_notas': grafico_distribuicao_notas,
        'grafico_top_livros': grafico_top_livros,
    }
    
    return render(request, 'dashboard.html', context)