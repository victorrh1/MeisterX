from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.usuarios.decorators import cliente_required
from .models import Produto, ProdutoEmpresa
from .forms import ProdutoForm, ProdutoEmpresaForm

@login_required
def lista(request):
    produtos = Produto.objects.all()
    return render(request, 'produtos/lista.html', {'produtos': produtos})

@login_required
def novo(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produto_lista')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/form.html', {'form': form, 'titulo': 'Novo'})

@login_required
def editar(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('produto_lista')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'produtos/form.html', {'form': form, 'titulo': 'Editar'})

@login_required
@cliente_required
def produto_empresa_lista(request):
    """
    Lista todos os produtos cadastrados pelo usuário cliente logado
    """
    try:
        produtos = ProdutoEmpresa.objects.filter(usuario_proprietario=request.user, ativo=True)
        total_estoque = sum(p.estoque for p in produtos if hasattr(p, 'estoque'))
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        produtos = []
        total_estoque = 0
        messages.error(request, "Ocorreu um erro ao buscar seus produtos. Entre em contato com o suporte.")
    
    context = {
        'produtos': produtos,
        'titulo': 'Meus Produtos',
        'subtitulo': 'Gerencie seu catálogo de produtos',
        'total_estoque': total_estoque
    }
    
    return render(request, 'produtos/produto_empresa_lista.html', context)

@login_required
@cliente_required
def produto_empresa_novo(request):
    """
    Cadastra um novo produto para o usuário cliente logado
    """
    if request.method == 'POST':
        form = ProdutoEmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.usuario_proprietario = request.user
            produto.save()
            
            # Adicionar o produto ao controle de estoque no dashboard
            # Configurar flag de sessão para notificar sobre o novo produto
            request.session['notificar_novo_produto'] = True
            
            messages.success(request, "Produto cadastrado com sucesso! O item foi adicionado ao controle de estoque.")
            return redirect('produto_empresa_lista')
    else:
        form = ProdutoEmpresaForm()
    
    context = {
        'form': form,
        'titulo': 'Cadastrar Produto',
        'subtitulo': 'Adicionar um novo produto',
        'botao': 'Cadastrar'
    }
    
    return render(request, 'produtos/produto_empresa_form.html', context)

@login_required
@cliente_required
def produto_empresa_editar(request, id):
    """
    Edita um produto existente do usuário cliente logado
    """
    produto = get_object_or_404(ProdutoEmpresa, id=id, usuario_proprietario=request.user)
    
    if request.method == 'POST':
        form = ProdutoEmpresaForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso! O controle de estoque foi atualizado.")
            return redirect('produto_empresa_lista')
    else:
        form = ProdutoEmpresaForm(instance=produto)
    
    context = {
        'form': form,
        'titulo': 'Editar Produto',
        'subtitulo': f'Editando {produto.nome}',
        'botao': 'Atualizar',
        'produto': produto
    }
    
    return render(request, 'produtos/produto_empresa_form.html', context)

@login_required
@cliente_required
def produto_empresa_excluir(request, id):
    """
    Exclui (marca como inativo) um produto do usuário cliente logado
    """
    produto = get_object_or_404(ProdutoEmpresa, id=id, usuario_proprietario=request.user)
    
    if request.method == 'POST':
        produto.ativo = False
        produto.save()
        messages.success(request, "Produto excluído com sucesso!")
        return redirect('produto_empresa_lista')
    
    context = {
        'produto': produto,
        'titulo': 'Confirmar Exclusão',
        'subtitulo': f'Tem certeza que deseja excluir o produto {produto.nome}?'
    }
    
    return render(request, 'produtos/produto_empresa_excluir.html', context) 