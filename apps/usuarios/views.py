from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import PerfilForm, CustomPasswordChangeForm
from .models import TwoFactorCode, Usuario, PerfilUsuario
from .decorators import admin_required, equipe_required, cliente_required
from apps.produtos.models import Produto
from apps.clientes.models import Cliente
from apps.dashboard.models import AssinaturaProduto
import json
import os
import random
from django.contrib.auth.models import Group
from django.db import transaction

# Funções de autenticação
def login_view(request):
    """
    Processa o login do usuário
    """
    # Se já estiver autenticado, redireciona para o dashboard apropriado
    if request.user.is_authenticated:
        return redirect('pos_login_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autenticar o usuário
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login bem-sucedido
            auth_login(request, user)
            messages.success(request, f"Bem-vindo, {user.first_name or username}!")
            
            # Verificar se o usuário tem 2FA habilitado
            if hasattr(user, 'two_factor_enabled') and user.two_factor_enabled:
                # Enviar código de verificação
                send_two_factor_code(user)
                
                # Preparar sessão para 2FA
                request.session['requires_2fa'] = True
                request.session['user_id_2fa'] = user.id
                
                return redirect('two_factor_verify')
            
            # Redirecionar para o dashboard apropriado
            return redirect('pos_login_redirect')
        else:
            # Login falhou
            messages.error(request, "Nome de usuário ou senha incorretos.")
    
    return render(request, 'registration/login.html')

def logout_view(request):
    """
    Processa o logout do usuário
    """
    # Fazer logout do usuário e limpar a sessão
    auth_logout(request)
    
    # Adicionando um log para depuração
    print("Logout realizado com sucesso")
    
    # Adicionar mensagem de sucesso para o usuário
    messages.success(request, "Você foi desconectado com sucesso.")
    
    # Garantir que o usuário seja redirecionado para a página de login com caminho absoluto
    response = redirect('/usuarios/login/')
    
    # Adicionar cabeçalhos para evitar cache
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@login_required
def meus_dados(request):
    """
    Exibe e permite edição dos dados cadastrais do usuário
    """
    # Obter dados do cliente, se existir
    cliente_data = None
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        cliente_data = {
            'nome_completo': cliente.nome_completo,
            'telefone': cliente.telefone,
            'endereco': cliente.endereco,
            'cidade': cliente.cidade,
            'estado': cliente.estado,
            'cep': cliente.cep,
            'data_cadastro': cliente.data_cadastro,
        }
    except Cliente.DoesNotExist:
        pass
    
    context = {
        'user': request.user,
        'cliente': cliente_data,
        'titulo': 'Meus Dados Cadastrais',
        'subtitulo': 'Visualize e edite suas informações cadastrais'
    }
    
    return render(request, 'usuarios/meus_dados.html', context)

@login_required
def meus_produtos(request):
    """
    Exibe os produtos adquiridos pelo usuário
    """
    # Buscar assinaturas do usuário
    assinaturas = []
    try:
        assinaturas = AssinaturaProduto.objects.filter(usuario=request.user).select_related('produto')
    except Exception as e:
        print(f"Erro ao buscar assinaturas: {e}")
    
    # Se não tem assinaturas, vamos mostrar os planos disponíveis para contratação
    planos_disponiveis = []
    if not assinaturas:
        # Definir os planos de assinatura disponíveis
        planos_disponiveis = [
            {
                'id': 1,  # Adicionando ID para o plano
                'nome': 'Plano Teste',
                'descricao': 'Experimente nossos serviços por 30 dias',
                'preco': 0,
                'periodo': '30 dias',
                'tipo': 'trial',
                'destaque': False,
                'recursos': [
                    {'nome': 'Acesso básico à plataforma', 'disponivel': True},
                    {'nome': '1 usuário permitido', 'disponivel': True},
                    {'nome': '5GB de armazenamento', 'disponivel': True},
                    {'nome': 'Suporte por email', 'disponivel': True},
                    {'nome': 'Exportação de dados', 'disponivel': False},
                    {'nome': 'API Access', 'disponivel': False},
                ],
                'cor': 'info'
            },
            {
                'id': 2,  # Adicionando ID para o plano
                'nome': 'Plano Profissional',
                'descricao': 'Ideal para pequenas empresas',
                'preco': 249,
                'periodo': 'por mês',
                'tipo': 'mensal',
                'destaque': True,
                'recursos': [
                    {'nome': 'Acesso completo à plataforma', 'disponivel': True},
                    {'nome': '5 usuários permitidos', 'disponivel': True},
                    {'nome': '50GB de armazenamento', 'disponivel': True},
                    {'nome': 'Suporte prioritário', 'disponivel': True},
                    {'nome': 'Exportação de dados', 'disponivel': True},
                    {'nome': 'API Access', 'disponivel': False},
                ],
                'cor': 'primary'
            },
            {
                'id': 3,  # Adicionando ID para o plano
                'nome': 'Plano Enterprise',
                'descricao': 'Solução completa para grandes empresas',
                'preco': 497,
                'periodo': 'por mês',
                'tipo': 'mensal',
                'destaque': False,
                'recursos': [
                    {'nome': 'Acesso completo à plataforma', 'disponivel': True},
                    {'nome': 'Usuários ilimitados', 'disponivel': True},
                    {'nome': '500GB de armazenamento', 'disponivel': True},
                    {'nome': 'Suporte 24/7', 'disponivel': True},
                    {'nome': 'Exportação de dados', 'disponivel': True},
                    {'nome': 'API Access', 'disponivel': True},
                ],
                'cor': 'success'
            }
        ]
    
    context = {
        'assinaturas': assinaturas,
        'planos_disponiveis': planos_disponiveis,
        'titulo': 'Meus Produtos',
        'subtitulo': 'Gerencie seus produtos e assinaturas'
    }
    
    return render(request, 'usuarios/meus_produtos.html', context)

@login_required
def minhas_compras(request):
    """
    Exibe as compras de materiais realizadas pelo usuário
    """
    # Nesta implementação inicial, vamos apenas mostrar um template simples
    # Em uma implementação real, buscaríamos as compras do banco de dados
    
    context = {
        'titulo': 'Minhas Compras',
        'subtitulo': 'Visualize suas compras de materiais e insumos'
    }
    
    return render(request, 'usuarios/minhas_compras.html', context)

class LoginRedirectMixin:
    """Mixin para redirecionar após login baseado no grupo do usuário"""
    def get_success_url(self):
        return self.request.user.get_dashboard_url()

class PerfilView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = PerfilForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PerfilForm(instance=request.user)
    return render(request, 'usuarios/perfil.html', {'form': form})

@admin_required
def admin_dashboard(request):
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
    
    context = {
        "labels": json.dumps(labels),
        "data": json.dumps(data),
    }
    return render(request, 'dashboard/admin.html', context)

@equipe_required
def equipe_dashboard(request):
    """
    View para o dashboard da equipe.
    """
    try:
        # Obtém lista de clientes ativos recentes
        clientes_ativos = Cliente.objects.filter(ativo=True).order_by('-data_cadastro')[:5]
    except:
        # Em caso de erro, retorna lista vazia
        clientes_ativos = []
        
    try:
        # Obtém lista de produtos recentes
        produtos_recentes = Produto.objects.all().order_by('-data_cadastro')[:5]
    except:
        # Em caso de erro, retorna lista vazia
        produtos_recentes = []
    
    # Contexto para os cards dinâmicos
    cards_context = {
        'cards': [
            {
                'title': 'Gerenciar Clientes',
                'description': 'Cadastrar e editar informações de clientes',
                'icon': 'fas fa-users',
                'color': 'primary',
                'url': 'cliente_lista'
            },
            {
                'title': 'Gerenciar Produtos',
                'description': 'Acessar e editar catálogo de produtos',
                'icon': 'fas fa-box',
                'color': 'success', 
                'url': 'produto_lista'
            },
            {
                'title': 'Relatórios',
                'description': 'Visualizar relatórios e análises',
                'icon': 'fas fa-chart-bar',
                'color': 'info',
                'url': 'relatorios'
            }
        ]
    }
    
    view_context = {
        'clientes_ativos': clientes_ativos,
        'produtos_recentes': produtos_recentes,
        'total_clientes': Cliente.objects.filter(ativo=True).count(),
        'view_context': cards_context
    }
    
    return render(request, 'dashboard/equipe.html', view_context)

@cliente_required
def cliente_dashboard(request):
    # Buscar produtos do cliente
    produtos_cliente = []
    try:
        # Em um sistema real, você buscaria produtos associados a este cliente
        # produtos_cliente = Produto.objects.filter(cliente=request.user)
        produtos_cliente = Produto.objects.all()[:3]  # Simulação para exemplo
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        produtos_cliente = []
    
    # Contexto para os cards dinâmicos
    cards = [
        {
            'title': 'Meus Produtos',
            'description': 'Produtos adquiridos',
            'icon': 'fa-box',
            'color': 'primary',
            'count': 'total_produtos_cliente',
            'url': '/usuarios/meus-produtos/'
        },
        {
            'title': 'Suporte',
            'description': 'Abrir um chamado de suporte',
            'icon': 'fa-headset',
            'color': 'info',
            'url': '#'
        },
        {
            'title': 'Minha Conta',
            'description': 'Informações da sua conta',
            'icon': 'fa-user',
            'color': 'success',
            'url': '/usuarios/perfil-usuario/'
        }
    ]
    
    total_produtos = len(produtos_cliente)
    
    # Contexto completo para o template
    context = {
        'produtos_cliente': produtos_cliente,
        'total_produtos_cliente': total_produtos,
        'dashboard_cards': cards,
        'view_context': {
            'total_produtos_cliente': total_produtos
        }
    }
    
    return render(request, 'dashboard/cliente.html', context)

@login_required
def dashboard(request):
    """View genérica que redireciona para o dashboard específico do usuário"""
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.is_equipe():
        return redirect('equipe_dashboard')
    elif request.user.is_cliente():
        return redirect('cliente_dashboard')
    return render(request, 'dashboard/default.html')

@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'usuarios/senha.html', {'form': form})

def two_factor_verify(request):
    if not request.session.get('requires_2fa'):
        return redirect('dashboard')

    if request.method == 'POST':
        code = request.POST.get('code')
        user_id = request.session.get('user_id_2fa')
        
        try:
            code_obj = TwoFactorCode.objects.get(
                user_id=user_id,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            # Marca o código como usado
            code_obj.is_used = True
            code_obj.save()
            
            # Completa o login
            user = code_obj.user
            auth_login(request, user)
            
            # Limpa a sessão
            del request.session['requires_2fa']
            del request.session['user_id_2fa']
            
            messages.success(request, 'Autenticação em duas etapas concluída com sucesso!')
            return redirect('dashboard')
            
        except TwoFactorCode.DoesNotExist:
            messages.error(request, 'Código inválido ou expirado.')
    
    return render(request, 'usuarios/two_factor_verify.html')

@login_required
def toggle_two_factor(request):
    user = request.user
    user.two_factor_enabled = not user.two_factor_enabled
    user.save()
    
    status = 'ativada' if user.two_factor_enabled else 'desativada'
    messages.success(request, f'Autenticação em duas etapas {status} com sucesso!')
    return redirect('perfil_usuario')

def send_two_factor_code(user):
    # Gera o código
    code = TwoFactorCode.generate_code()
    
    # Salva o código no banco
    TwoFactorCode.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10)
    )
    
    # Envia o email
    send_mail(
        'Seu código de verificação',
        f'Seu código de verificação é: {code}\nEste código expira em 10 minutos.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def pos_login_redirect(request):
    """
    Redireciona o usuário para o dashboard apropriado baseado no seu grupo
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        if request.user.groups.filter(name='Cliente').exists():
            return redirect('cliente_dashboard')
        elif request.user.groups.filter(name='Equipe').exists():
            return redirect('equipe_dashboard')
        elif request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        else:
            # Se não tiver grupo, redireciona para o dashboard padrão
            return redirect('dashboard')
    except Exception as e:
        print(f"Erro ao redirecionar após login: {e}")
        return redirect('dashboard')

@login_required
def perfil_usuario(request):
    """
    Exibe e processa o formulário de perfil do usuário
    """
    # Verificar se o template existe e registrar para depuração
    template_path = os.path.join('templates', 'usuarios', 'perfil_usuario.html')
    print(f"Template existe? {os.path.exists(template_path)}")
    
    if request.method == 'POST':
        # Processar os dados do formulário
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Atualizar os dados do usuário
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        
        # Verificar se o e-mail mudou
        if email and email != user.email:
            user.email = email
        
        # Salvar alterações
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
        # Adicionar cabeçalhos para evitar cache
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    except Exception as e:
        print(f"Erro ao renderizar o template: {e}")
        messages.error(request, "Erro ao carregar a página de perfil")
        return redirect('dashboard')

@login_required
def notificacoes(request):
    """
    Exibe as notificações do usuário
    """
    notificacoes = []
    try:
        notificacoes = Notification.objects.filter(user=request.user).order_by('-created_at')
    except Exception as e:
        print(f"Erro ao buscar notificações: {e}")

    context = {
        'notificacoes': notificacoes,
        'titulo': 'Minhas Notificações',
        'subtitulo': 'Visualize suas notificações recentes'
    }
    
    return render(request, 'usuarios/notificacoes.html', context)

@login_required
def gerenciar_assinatura(request, id):
    """
    Permite gerenciar uma assinatura específica
    """
    try:
        assinatura = AssinaturaProduto.objects.get(id=id, usuario=request.user)
    except AssinaturaProduto.DoesNotExist:
        messages.error(request, "Assinatura não encontrada ou você não tem permissão para acessá-la.")
        return redirect('meus_produtos')
    
    # Processar mudança de renovação automática via POST
    if request.method == 'POST':
        if 'renovacao_automatica' in request.POST:
            renovacao_automatica = request.POST.get('renovacao_automatica') == 'on'
            assinatura.renovacao_automatica = renovacao_automatica
            assinatura.save(update_fields=['renovacao_automatica'])
            
            status = "ativada" if renovacao_automatica else "desativada"
            messages.success(request, f"Renovação automática {status} com sucesso!")
            
            # Redirecionar para a mesma página para evitar reenvio do formulário
            return redirect('gerenciar_assinatura', id=id)
    
    context = {
        'assinatura': assinatura,
        'titulo': f'Gerenciar {assinatura.produto.nome}',
        'subtitulo': 'Gerencie os detalhes da sua assinatura'
    }
    
    return render(request, 'usuarios/gerenciar_assinatura.html', context)

@login_required
def renovar_assinatura(request, id):
    """
    Renova uma assinatura específica
    """
    try:
        assinatura = AssinaturaProduto.objects.get(id=id, usuario=request.user)
        
        # Renovar a assinatura usando o método definido no modelo
        assinatura.renovar()
        
        # Atualizar a flag de renovação automática para true
        assinatura.renovacao_automatica = True
        assinatura.save(update_fields=['renovacao_automatica'])
        
        messages.success(request, f"Assinatura de '{assinatura.produto.nome}' renovada com sucesso! Nova data de expiração: {assinatura.data_expiracao.strftime('%d/%m/%Y')}")
    except AssinaturaProduto.DoesNotExist:
        messages.error(request, "Assinatura não encontrada ou você não tem permissão para renová-la.")
    except Exception as e:
        messages.error(request, f"Erro ao renovar assinatura: {str(e)}")
    
    return redirect('meus_produtos')

@login_required
def cancelar_assinatura(request, id):
    """
    Cancela uma assinatura específica
    """
    try:
        assinatura = AssinaturaProduto.objects.get(id=id, usuario=request.user)
        
        # Verificar se não está já cancelada
        if assinatura.status == 'cancelado':
            messages.info(request, "Esta assinatura já está cancelada.")
            return redirect('meus_produtos')
        
        # Cancelar a assinatura usando o método definido no modelo
        assinatura.cancelar()
        
        messages.success(request, f"Assinatura de '{assinatura.produto.nome}' cancelada com sucesso.")
    except AssinaturaProduto.DoesNotExist:
        messages.error(request, "Assinatura não encontrada ou você não tem permissão para cancelá-la.")
    except Exception as e:
        messages.error(request, f"Erro ao cancelar assinatura: {str(e)}")
    
    return redirect('meus_produtos')

@login_required
def iniciar_trial(request, id):
    """
    Inicia uma assinatura de teste (trial) para um plano
    """
    try:
        produto = Produto.objects.get(id=id)
        
        # Verificar se já existe uma assinatura para este produto
        if AssinaturaProduto.objects.filter(usuario=request.user, produto=produto).exists():
            messages.info(request, f"Você já possui uma assinatura para '{produto.nome}'")
            return redirect('meus_produtos')
        
        # Criar uma nova assinatura trial
        data_expiracao = timezone.now() + timezone.timedelta(days=30)  # Trial de 30 dias
        
        AssinaturaProduto.objects.create(
            usuario=request.user,
            produto=produto,
            data_inicio=timezone.now(),
            data_expiracao=data_expiracao,
            renovacao_automatica=False,  # Trial não renova automaticamente
            status='ativo'
        )
        
        messages.success(request, f"Período de teste para '{produto.nome}' iniciado com sucesso!")
    except Produto.DoesNotExist:
        messages.error(request, "Plano não encontrado.")
    except Exception as e:
        messages.error(request, f"Erro ao iniciar período de teste: {str(e)}")
    
    return redirect('meus_produtos')

@login_required
def contratar_plano(request, id):
    """
    Contrata um plano pago
    """
    try:
        produto = Produto.objects.get(id=id)
        
        # Verificar se já existe uma assinatura para este produto
        if AssinaturaProduto.objects.filter(usuario=request.user, produto=produto).exists():
            messages.info(request, f"Você já possui uma assinatura para '{produto.nome}'")
            return redirect('meus_produtos')
        
        # Em um ambiente real, aqui seria integrado o processo de pagamento
        # Por enquanto, apenas simularemos uma contratação bem-sucedida
        
        # Criar uma nova assinatura
        data_expiracao = timezone.now() + timezone.timedelta(days=produto.duracao_dias)
        
        AssinaturaProduto.objects.create(
            usuario=request.user,
            produto=produto,
            data_inicio=timezone.now(),
            data_expiracao=data_expiracao,
            renovacao_automatica=True,  # Assinaturas pagas renovam automaticamente por padrão
            status='ativo'
        )
        
        messages.success(request, f"Assinatura de '{produto.nome}' contratada com sucesso!")
    except Produto.DoesNotExist:
        messages.error(request, "Plano não encontrado.")
    except Exception as e:
        messages.error(request, f"Erro ao contratar plano: {str(e)}")
    
    return redirect('meus_produtos')

@login_required
def pagamentos(request):
    """
    Exibe e gerencia informações de pagamento do usuário
    """
    context = {
        'titulo': 'Informações de Pagamento',
        'subtitulo': 'Gerencie seus métodos de pagamento e histórico de transações'
    }
    
    return render(request, 'usuarios/pagamentos.html', context)

@login_required
def contato(request):
    """
    Página de contato para suporte
    """
    if request.method == 'POST':
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        
        if assunto and mensagem:
            # Em um ambiente real, aqui seria enviado um e-mail ou criado um ticket
            # Por enquanto, apenas simulamos o envio bem-sucedido
            messages.success(request, "Sua mensagem foi enviada com sucesso! Nossa equipe entrará em contato em breve.")
            return redirect('contato')
        else:
            messages.error(request, "Por favor, preencha todos os campos.")
    
    context = {
        'titulo': 'Fale Conosco',
        'subtitulo': 'Estamos aqui para ajudar'
    }
    
    return render(request, 'usuarios/contato.html', context)

def register(request):
    if request.method == 'POST':
        # Debugging
        print(f"POST data: {request.POST}")
        print(f"Terms value: {request.POST.get('terms')}")
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        terms = request.POST.get('terms') == 'on'
        
        print(f"Terms evaluated: {terms}")
        
        # Validações básicas
        if not all([first_name, last_name, email, username, password, password_confirm]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('register')
        
        if not terms:
            messages.error(request, 'Você deve aceitar os termos de uso para criar uma conta.')
            return redirect('register')
            
        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('register')
            
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return redirect('register')
            
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return redirect('register')
            
        try:
            with transaction.atomic():
                # Criar usuário
                user = Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True  # Usuário ativo, mas sem permissões
                )
                
                # Criar perfil do usuário
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    is_approved=False,
                    pending_approval=True
                )
                
                # Alteração: Não fazer login automático após o registro
                # e ir direto para a tela de login com uma mensagem
                messages.success(request, 'Conta criada com sucesso! Aguarde aprovação pelo administrador. Por favor, faça login.')
                return redirect('login')
                
        except Exception as e:
            print(f"Erro ao criar usuário: {str(e)}")
            messages.error(request, 'Ocorreu um erro ao criar sua conta. Por favor, tente novamente.')
            return redirect('register')
            
    return render(request, 'registration/register.html')

@admin_required
def admin_usuarios(request):
    """
    Lista todos os usuários para o administrador gerenciar
    """
    usuarios_pendentes = PerfilUsuario.objects.filter(pending_approval=True).select_related('user')
    usuarios_aprovados = PerfilUsuario.objects.filter(pending_approval=False, is_approved=True).select_related('user')
    
    context = {
        'usuarios_pendentes': usuarios_pendentes,
        'usuarios_aprovados': usuarios_aprovados,
        'titulo': 'Gerenciar Usuários',
        'subtitulo': 'Aprove ou gerencie o acesso de usuários'
    }
    
    return render(request, 'usuarios/admin_usuarios.html', context)

@admin_required
def aprovar_usuario(request, user_id):
    """
    Permite a um administrador aprovar um usuário pendente
    """
    try:
        perfil = PerfilUsuario.objects.get(user_id=user_id, pending_approval=True)
        usuario = perfil.user
        
        if request.method == 'POST':
            # Aprovar o usuário
            perfil.is_approved = True
            perfil.pending_approval = False
            perfil.approved_at = timezone.now()
            perfil.save()
            
            # Adicionar ao grupo Cliente
            grupo_cliente, created = Group.objects.get_or_create(name='Cliente')
            usuario.groups.add(grupo_cliente)
            
            messages.success(request, f'Usuário {usuario.username} aprovado com sucesso!')
            
            # Enviar e-mail de notificação (opcional)
            try:
                subject = 'Sua conta foi aprovada!'
                message = f'Olá {usuario.get_full_name() or usuario.username},\n\nSua conta no Gerencial SaaS foi aprovada. Agora você pode acessar todas as funcionalidades da plataforma.\n\nAtenciosamente,\nEquipe Gerencial SaaS'
                from_email = settings.DEFAULT_FROM_EMAIL
                usuario.email_user(subject, message, from_email)
            except Exception as e:
                # Se falhar o envio do email, apenas loga o erro
                print(f"Erro ao enviar e-mail para {usuario.email}: {e}")
            
            return redirect('admin_usuarios')
        
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'titulo': 'Aprovar Usuário',
            'subtitulo': f'Aprovar acesso para {usuario.get_full_name() or usuario.username}'
        }
        
        return render(request, 'usuarios/aprovar_usuario.html', context)
    
    except PerfilUsuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado ou já aprovado.')
        return redirect('admin_usuarios')

@admin_required
def rejeitar_usuario(request, user_id):
    """
    Permite a um administrador rejeitar um usuário pendente
    """
    try:
        perfil = PerfilUsuario.objects.get(user_id=user_id, pending_approval=True)
        usuario = perfil.user
        
        if request.method == 'POST':
            # Marcar o perfil como rejeitado
            perfil.is_approved = False
            perfil.pending_approval = False
            perfil.rejected_at = timezone.now()
            perfil.save()
            
            # Desativar a conta do usuário
            usuario.is_active = False
            usuario.save()
            
            messages.success(request, f'Usuário {usuario.username} rejeitado com sucesso.')
            
            # Enviar e-mail de notificação (opcional)
            try:
                subject = 'Seu cadastro não foi aprovado'
                message = f'Olá {usuario.get_full_name() or usuario.username},\n\nInfelizmente, seu cadastro no Gerencial SaaS não foi aprovado. Se você acredita que houve um erro, entre em contato com nossa equipe de suporte.\n\nAtenciosamente,\nEquipe Gerencial SaaS'
                from_email = settings.DEFAULT_FROM_EMAIL
                usuario.email_user(subject, message, from_email)
            except Exception as e:
                # Se falhar o envio do email, apenas loga o erro
                print(f"Erro ao enviar e-mail para {usuario.email}: {e}")
            
            # Se a solicitação veio do dashboard
            referer = request.META.get('HTTP_REFERER', '')
            if 'dashboard/admin' in referer:
                return redirect('admin_dashboard')
            
            return redirect('admin_usuarios')
            
        context = {
            'usuario': usuario,
            'perfil': perfil,
            'titulo': 'Rejeitar Usuário',
            'subtitulo': f'Rejeitar acesso para {usuario.get_full_name() or usuario.username}'
        }
        
        return render(request, 'usuarios/rejeitar_usuario.html', context)
    
    except PerfilUsuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado ou já processado.')
        
        # Se a solicitação veio do dashboard
        referer = request.META.get('HTTP_REFERER', '')
        if 'dashboard/admin' in referer:
            return redirect('admin_dashboard')
        
        return redirect('admin_usuarios')
