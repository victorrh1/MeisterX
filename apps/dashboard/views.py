from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from datetime import timedelta
import json
from apps.clientes.models import Cliente
from apps.produtos.models import Produto as ProdutoSimples, ProdutoEmpresa
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
import csv
import io
from apps.dashboard.models import CategoriaPlano, Produto
from django.utils.text import slugify
import os
from apps.usuarios.models import PerfilUsuario, Usuario
import random

def is_admin(user):
    return user.groups.filter(name='Admin').exists()

def is_equipe(user):
    return user.groups.filter(name='Equipe').exists()

def is_cliente(user):
    return user.groups.filter(name='Cliente').exists()

def calcular_crescimento(model):
    hoje = timezone.now()
    primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    primeiro_dia_mes_anterior = (primeiro_dia_mes - timedelta(days=1)).replace(day=1)
    
    # Determina qual campo de data usar
    campo_data = 'data_cadastro' if model == Cliente else 'data_criacao'
    
    try:
        total_atual = model.objects.filter(**{f"{campo_data}__gte": primeiro_dia_mes}).count()
        total_anterior = model.objects.filter(**{
            f"{campo_data}__gte": primeiro_dia_mes_anterior,
            f"{campo_data}__lt": primeiro_dia_mes
        }).count()
        
        if total_anterior == 0:
            return 100 if total_atual > 0 else 0
        
        percentual = ((total_atual - total_anterior) / total_anterior) * 100
        return int(percentual)
    except:
        return 0

def export_csv(data, filename):
    """
    Função auxiliar para exportar dados em CSV
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Criar o writer do CSV e escrever os dados
    writer = csv.writer(response)
    for row in data:
        writer.writerow(row)
    
    return response

def export_pdf(data, filename):
    """
    Função auxiliar para exportar dados em PDF (simplesmente redireciona no momento)
    """
    # Aqui viria o código para gerar o PDF
    # Como é apenas um exemplo, redirecionamos
    return None  # Substituir por código real quando disponível

@login_required
@user_passes_test(is_cliente)
def exportar_relatorio(request, format):
    """
    Exporta dados do cliente em formato CSV ou PDF
    """
    # Buscar produtos do cliente (simulação)
    try:
        produtos_cliente = Produto.objects.all()[:5]  # Simulação para exemplo
    except:
        produtos_cliente = []
    
    # Preparar dados para exportação
    hoje = timezone.now()
    
    # Preparar tabela de produtos
    data_produtos = []
    data_produtos.append(['Nome do Produto', 'Data de Compra', 'Status', 'Último Acesso'])  # Cabeçalho
    
    for produto in produtos_cliente:
        data_produtos.append([
            produto.nome, 
            '20/04/2025',  # Data simulada
            'Ativo',
            (hoje - timedelta(days=produto.id % 10)).strftime('%d/%m/%Y')  # Último acesso simulado
        ])
    
    # Exportar conforme formato solicitado
    if format.lower() == 'csv':
        return export_csv(data_produtos, 'produtos_cliente.csv')
    else:
        # Qualquer outro formato redireciona para o dashboard
        messages.warning(request, "Formato de exportação não disponível no momento.")
        return redirect('cliente_dashboard')

# Views para os dashboards específicos por tipo de usuário
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Dashboard para administradores
    """
    # Dados para o gráfico de vendas dos últimos 7 dias
    hoje = timezone.now().date()
    dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]
    
    labels = [d.strftime("%d/%m") for d in dias]
    data = []
    
    # Dados simulados para o exemplo
    # Em um ambiente real, você usaria algo como:
    # for d in dias:
    #     total = Venda.objects.filter(data__date=d).count()
    #     data.append(total)
    
    # Simulando dados aleatórios para o exemplo
    for _ in dias:
        data.append(random.randint(5, 20))
    
    # Obter usuários pendentes e aprovados para o dashboard
    usuarios_pendentes = PerfilUsuario.objects.filter(
        pending_approval=True, 
        is_approved=False
    ).select_related('user').order_by('-registration_date')[:10]
    
    usuarios_aprovados = PerfilUsuario.objects.filter(
        pending_approval=False, 
        is_approved=True
    ).select_related('user').order_by('-approval_date')[:10]
    
    # Obter todos os usuários do grupo Cliente
    from django.contrib.auth.models import Group
    
    try:
        grupo_cliente = Group.objects.get(name='Cliente')
        clientes_usuarios = Usuario.objects.filter(groups=grupo_cliente).order_by('-date_joined')
    except Group.DoesNotExist:
        clientes_usuarios = []
    
    context = {
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "usuarios_pendentes": usuarios_pendentes,
        "usuarios_aprovados": usuarios_aprovados,
        "clientes_usuarios": clientes_usuarios,
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
@user_passes_test(is_equipe)
def equipe_dashboard(request):
    """
    Dashboard para membros da equipe
    """
    try:
        clientes = Cliente.objects.all()[:5]
    except:
        clientes = []
        
    try:
        produtos = Produto.objects.all()[:5]
    except:
        produtos = []
    
    context = {
        'total_clientes': Cliente.objects.count() if 'Cliente' in globals() else 0,
        'total_produtos': Produto.objects.count() if 'Produto' in globals() else 0,
        'clientes_ativos': clientes,
        'produtos_recentes': produtos,
        'tarefas': 3  # Exemplo, idealmente seria um model real
    }
    
    return render(request, 'dashboard/equipe.html', context)

@login_required
@user_passes_test(is_cliente)
def cliente_dashboard(request):
    """
    Dashboard para clientes
    """
    # Limpar todas as mensagens de erro da sessão
    storage = messages.get_messages(request)
    # Itera sobre as mensagens para marcá-las como lidas
    for message in storage:
        pass
    # Limpa o storage
    storage.used = True
    
    # Verificar se há novos produtos a serem notificados
    # Em um sistema real, você verificaria produtos adicionados desde o último login
    mostrar_notificacao = request.session.get('notificar_novo_produto', False)
    if mostrar_notificacao:
        messages.success(request, "Novo produto cadastrado!")
        # Limpar o flag após exibir a notificação
        request.session['notificar_novo_produto'] = False
    
    # Obter produtos cadastrados pelo cliente
    produtos_empresa = []
    try:
        produtos_empresa = ProdutoEmpresa.objects.filter(
            usuario_proprietario=request.user, 
            ativo=True
        ).order_by('-data_cadastro')
    except Exception as e:
        print(f"Erro ao buscar produtos da empresa: {e}")
    
    # Exemplo: em um sistema real, você buscaria apenas os produtos do cliente
    produtos_cliente = []
    try:
        # Substituir por sua lógica real de busca de produtos do cliente
        # produtos_cliente = Produto.objects.filter(cliente=request.user)
        produtos_cliente = Produto.objects.all()[:3]  # Simulação para exemplo
        
        # Adicionar produtos da empresa junto com os produtos normais
        # para exibição no controle de estoque
        produtos_controle_estoque = list(produtos_cliente)
        produtos_controle_estoque.extend(produtos_empresa)
    except Exception as e:
        print(f"Erro ao buscar produtos do cliente: {e}")
        produtos_cliente = []
        produtos_controle_estoque = list(produtos_empresa)
    
    context = {
        'produtos_cliente': produtos_cliente,
        'produtos_empresa': produtos_empresa[:5],  # Limitar a 5 produtos mais recentes
        'produtos_controle_estoque': produtos_controle_estoque[:10],  # Limitar a 10 no total
        'total_estoque': sum(p.estoque for p in produtos_empresa if hasattr(p, 'estoque')),
        'view_context': {
            'total_produtos_cliente': len(produtos_cliente),
            'total_produtos_empresa': len(produtos_empresa)
        }
    }
    
    return render(request, 'dashboard/cliente.html', context)

@login_required
def dashboard(request):
    """
    Dashboard genérico que redireciona com base no tipo de usuário
    """
    if is_admin(request.user):
        try:
            clientes = Cliente.objects.all()[:5]
        except:
            clientes = []
            
        try:
            produtos = Produto.objects.all()[:5]
        except:
            produtos = []
        
        # Dados para o gráfico de vendas (simulados)
        hoje = timezone.now()
        labels = []
        data = []
        
        # Simulando dados de vendas dos últimos 6 meses
        for i in range(6, 0, -1):
            mes_atual = hoje - timedelta(days=30 * i)
            labels.append(mes_atual.strftime('%b/%Y'))
            data.append(10 + i * 5)  # Valores simulados
        
        view_context = {
            'total_clientes': Cliente.objects.count() if 'Cliente' in globals() else 0,
            'total_produtos': Produto.objects.count() if 'Produto' in globals() else 0,
            'clientes_ativos': clientes,
            'produtos_recentes': produtos,
            'labels': json.dumps(labels),
            'data': json.dumps(data),
        }
        
        return render(request, 'dashboard/index.html', view_context)
        
    elif is_equipe(request.user):
        try:
            clientes = Cliente.objects.all()[:5]
        except:
            clientes = []
            
        try:
            produtos = Produto.objects.all()[:5]
        except:
            produtos = []
        
        context = {
            'total_clientes': Cliente.objects.count() if 'Cliente' in globals() else 0,
            'total_produtos': Produto.objects.count() if 'Produto' in globals() else 0,
            'clientes_ativos': clientes,
            'produtos_recentes': produtos,
            'tarefas': 3  # Exemplo
        }
        
        return render(request, 'dashboard/equipe.html', context)
        
    elif is_cliente(request.user):
        # Limpar mensagens da sessão
        storage = messages.get_messages(request)
        for message in storage:
            pass
        storage.used = True
        
        # Verificar notificações
        mostrar_notificacao = request.session.get('notificar_novo_produto', False)
        if mostrar_notificacao:
            messages.success(request, "Novo produto cadastrado!")
            request.session['notificar_novo_produto'] = False
        
        # Obter produtos do cliente
        produtos_empresa = []
        try:
            produtos_empresa = ProdutoEmpresa.objects.filter(
                usuario_proprietario=request.user, 
                ativo=True
            ).order_by('-data_cadastro')
        except Exception as e:
            print(f"Erro ao buscar produtos da empresa: {e}")
        
        produtos_cliente = []
        try:
            produtos_cliente = Produto.objects.all()[:3]
            produtos_controle_estoque = list(produtos_cliente)
            produtos_controle_estoque.extend(produtos_empresa)
        except Exception as e:
            print(f"Erro ao buscar produtos do cliente: {e}")
            produtos_cliente = []
            produtos_controle_estoque = list(produtos_empresa)
        
        context = {
            'produtos_cliente': produtos_cliente,
            'produtos_empresa': produtos_empresa[:5],
            'produtos_controle_estoque': produtos_controle_estoque[:10],
            'total_estoque': sum(p.estoque for p in produtos_empresa if hasattr(p, 'estoque')),
            'view_context': {
                'total_produtos_cliente': len(produtos_cliente),
                'total_produtos_empresa': len(produtos_empresa)
            }
        }
        
        return render(request, 'dashboard/cliente.html', context)
    
    # Se não encontrou nenhum grupo conhecido, exibe um dashboard padrão
    context = {}
    return render(request, 'dashboard/default.html', context)

@login_required
@user_passes_test(is_equipe)
def painel_equipe(request):
    """View legada - para compatibilidade"""
    return redirect('equipe_dashboard')

@login_required
@user_passes_test(is_cliente)
def painel_cliente(request):
    """View legada - para compatibilidade"""
    return redirect('cliente_dashboard')

@login_required
def notificacoes(request):
    """
    Exibe as notificações do usuário
    """
    from apps.core.models import Notification
    
    # Buscar notificações do usuário atual
    notificacoes_user = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Marcar as notificações como lidas
    if 'marcar_lidas' in request.GET:
        for notificacao in notificacoes_user.filter(lida=False):
            notificacao.lida = True
            notificacao.save()
        messages.success(request, "Todas as notificações foram marcadas como lidas.")
        return redirect('notificacoes')
    
    context = {
        'notificacoes': notificacoes_user,
        'total_nao_lidas': notificacoes_user.filter(lida=False).count()
    }
    
    return render(request, 'dashboard/notificacoes.html', context)

def cadastrar_produto_demo(request):
    """
    Função para cadastrar um novo produto no sistema
    """
    # Buscar categorias para o dropdown
    categorias = CategoriaPlano.objects.filter(ativo=True)
    
    # Adicionar logs para depuração
    print(f"Request method: {request.method}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    
    if request.method == 'POST':
        # Extrair dados do formulário
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        preco = request.POST.get('preco')
        
        # Logs de depuração para valores recebidos
        print(f"Nome: {nome}")
        print(f"Descrição: {descricao}")
        print(f"Preço: {preco}")
        
        # Validação básica
        if not all([nome, descricao, preco]):
            messages.warning(request, "Preencha todos os campos obrigatórios.")
            return render(request, 'dashboard/cadastrar_produto.html', {'categorias': categorias})
        
        try:
            # Criar slug a partir do nome
            slug = slugify(nome)
            
            # Processar campos opcionais ou com valores padrão
            categoria_id = request.POST.get('categoria')
            categoria = None
            if categoria_id:
                try:
                    categoria = CategoriaPlano.objects.get(id=categoria_id)
                except CategoriaPlano.DoesNotExist:
                    pass
            
            # Valores booleanos de checkboxes
            permite_exportacao = 'permite_exportacao' in request.POST
            permite_api = 'permite_api' in request.POST
            suporte_24h = 'suporte_24h' in request.POST
            
            # Valores numéricos
            try:
                duracao_dias = int(request.POST.get('duracao_dias', 30))
                usuarios_permitidos = int(request.POST.get('usuarios_permitidos', 1))
                armazenamento_gb = int(request.POST.get('armazenamento_gb', 5))
                # Compatibilidade com o modelo de produtos simples
                estoque = int(request.POST.get('estoque', 0))
            except (ValueError, TypeError):
                messages.error(request, "Valores numéricos inválidos fornecidos.")
                return render(request, 'dashboard/cadastrar_produto.html', {'categorias': categorias})
            
            # Campos de texto
            tipo = request.POST.get('tipo', 'assinatura')
            descricao_curta = nome if len(nome) < 255 else nome[:252] + '...'
            
            # Processamento da imagem
            imagem = request.FILES.get('imagem')
            
            # Criar o produto usando o modelo Dashboard
            novo_produto = Produto.objects.create(
                nome=nome,
                slug=slug,
                descricao=descricao,
                descricao_curta=descricao_curta,
                preco=float(preco),
                tipo=tipo,
                categoria=categoria,
                duracao_dias=duracao_dias,
                usuarios_permitidos=usuarios_permitidos,
                armazenamento_gb=armazenamento_gb,
                permite_exportacao=permite_exportacao,
                permite_api=permite_api,
                suporte_24h=suporte_24h,
                imagem=imagem
            )
            
            # Para compatibilidade, também criar no modelo simples
            try:
                produto_simples = ProdutoSimples.objects.create(
                    nome=nome,
                    descricao=descricao,
                    preco=float(preco),
                    estoque=estoque,
                )
            except Exception as e:
                # Se falhar a criação do produto simples, registramos mas continuamos
                print(f"Erro ao criar produto simples: {str(e)}")
            
            # Definir flag para notificar na próxima visita ao dashboard
            request.session['notificar_novo_produto'] = True
            
            # Criar uma notificação no banco de dados
            from apps.core.models import Notification
            
            # Em um sistema real, você enviaria notificações apenas para usuários relevantes
            from django.contrib.auth.models import Group
            try:
                grupo_clientes = Group.objects.get(name='Cliente')
                clientes = User.objects.filter(groups=grupo_clientes)
                
                for cliente in clientes:
                    Notification.objects.create(
                        user=cliente,
                        title='Novo Produto Disponível',
                        message=f'O produto "{nome}" está disponível para compra. Preço: R$ {preco}',
                    )
            except Exception as e:
                # Se falhar a criação das notificações, registramos mas continuamos
                print(f"Erro ao criar notificações: {str(e)}")
            
            messages.success(request, f"Produto '{nome}' cadastrado com sucesso!")
            return redirect('cliente_dashboard')
            
        except Exception as e:
            # Log detalhado da exceção para depuração
            import traceback
            print(f"Erro ao cadastrar produto: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Erro ao cadastrar produto: {str(e)}")
    
    # Renderizar o formulário de cadastro
    context = {
        'categorias': categorias
    }
    return render(request, 'dashboard/cadastrar_produto.html', context)

@login_required
def perfil_usuario(request):
    # Verificar se o template existe
    template_path = os.path.join('templates', 'usuarios', 'perfil_usuario.html')
    
    if request.method == 'POST':
        # Processar os dados do formulário
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Atualizar os dados do usuário
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        
        if email and email != user.email:
            user.email = email
        
        user.save()
        
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('perfil_usuario')
    
    # Renderizar o template
    context = {
        'titulo': 'Meu Perfil',
        'subtitulo': 'Atualize suas informações pessoais',
        'user': request.user
    }
    
    try:
        response = render(request, 'usuarios/perfil_usuario.html', context)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except Exception as e:
        print(f"Erro ao renderizar o template: {e}")
        messages.error(request, "Erro ao carregar a página de perfil")
        return redirect('dashboard')

@login_required
def dashboard_pendente(request):
    """
    Dashboard para usuários com acesso pendente de aprovação
    """
    try:
        perfil = PerfilUsuario.objects.get(user=request.user)
        if not perfil.pending_approval:
            # Se não está mais pendente, redireciona para o dashboard apropriado
            return redirect('pos_login_redirect')
    except PerfilUsuario.DoesNotExist:
        # Se não tem perfil, cria um pendente
        perfil = PerfilUsuario.objects.create(
            user=request.user,
            is_approved=False,
            pending_approval=True
        )
    
    context = {
        'titulo': 'Acesso Pendente',
        'subtitulo': 'Aguardando aprovação do administrador'
    }
    
    return render(request, 'dashboard/pendente.html', context)
