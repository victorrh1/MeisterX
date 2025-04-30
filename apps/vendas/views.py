from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Sum, F, DecimalField
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from django.core.exceptions import ValidationError
import re

# Comentando o import do decorador cliente_required, pois não vamos mais usá-lo
# from apps.usuarios.decorators import cliente_required
from apps.produtos.models import ProdutoEmpresa
from apps.clientes.models import ClienteEmpresa, Endereco
from .models import Venda, ItemVenda, FormaPagamento, MetodoEnvio, StatusVenda

@login_required
def venda_lista(request):
    """
    Lista todas as vendas realizadas pelo usuário, organizadas por abas
    """
    try:
        # Obter todas as vendas do usuário
        vendas = Venda.objects.filter(usuario_vendedor=request.user).order_by('-data_venda')
        
        # Separar vendas por categoria para as abas
        vendas_recentes = vendas.filter(
            status__in=[
                StatusVenda.RASCUNHO.value,
                StatusVenda.PENDENTE.value,
                StatusVenda.PAGO.value
            ]
        ).order_by('-data_venda')[:6]  # Limitar a 6 vendas mais recentes
        
        vendas_processamento = vendas.filter(
            status__in=[
                StatusVenda.PAGO.value,
                StatusVenda.ENVIADO.value
            ]
        ).order_by('-data_venda')
        
        vendas_historico = vendas.filter(
            status__in=[
                StatusVenda.ENTREGUE.value,
                StatusVenda.CANCELADO.value
            ]
        ).order_by('-data_venda')
        
        vendas_envio = vendas.filter(
            status__in=[
                StatusVenda.PAGO.value,
                StatusVenda.ENVIADO.value,
                StatusVenda.ENTREGUE.value
            ]
        ).order_by('-data_venda')
        
    except Exception as e:
        # Se houver qualquer erro no banco de dados, exibir listas vazias
        vendas = []
        vendas_recentes = []
        vendas_processamento = []
        vendas_historico = []
        vendas_envio = []
        messages.warning(request, f"Não foi possível carregar as vendas. Erro: {str(e)}")
    
    # Dados do contexto para o template
    context = {
        'vendas': vendas,
        'vendas_recentes': vendas_recentes,
        'vendas_processamento': vendas_processamento,
        'vendas_historico': vendas_historico,
        'vendas_envio': vendas_envio,
        'titulo': 'Minhas Vendas',
        'subtitulo': 'Gerencie suas vendas',
        # Valores vazios para os cálculos no template
        'total_vendas': 0,
        'valor_total': 0,
        'ticket_medio': 0,
        'vendas_por_status': {
            'pendente': 0,
            'pago': 0,
            'enviado': 0,
            'entregue': 0,
            'cancelado': 0
        }
    }
    
    # Se conseguimos carregar as vendas, calcular estatísticas
    if vendas:
        try:
            context['total_vendas'] = vendas.count()
            context['valor_total'] = sum(venda.valor_total for venda in vendas)
            
            if context['total_vendas'] > 0:
                context['ticket_medio'] = context['valor_total'] / context['total_vendas']
            
            # Contar vendas por status
            for status in StatusVenda:
                count = vendas.filter(status=status.value).count()
                context['vendas_por_status'][status.value] = count
        except Exception as e:
            # Se houve erro nos cálculos, ignorar
            pass
    
    return render(request, 'vendas/venda_lista.html', context)

@login_required
def venda_detalhe(request, id):
    """
    Exibe os detalhes de uma venda específica
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    context = {
        'venda': venda,
        'itens': venda.itens.all(),
        'titulo': f'Venda #{venda.id}',
        'subtitulo': f'Detalhes da venda realizada em {venda.data_venda.strftime("%d/%m/%Y")}'
    }
    
    return render(request, 'vendas/venda_detalhe.html', context)

@login_required
def venda_nova(request):
    """
    Cria uma nova venda
    """
    # Obter formas de pagamento e métodos de envio ativos
    formas_pagamento = FormaPagamento.objects.filter(ativo=True)
    metodos_envio = MetodoEnvio.objects.filter(ativo=True)
    clientes = ClienteEmpresa.objects.filter(usuario_proprietario=request.user, ativo=True)
    produtos = ProdutoEmpresa.objects.filter(usuario_proprietario=request.user, ativo=True)
    
    # Se não tiver formas de pagamento ou métodos de envio, redireciona e avisa
    if not formas_pagamento.exists():
        messages.warning(request, "É necessário cadastrar formas de pagamento antes de criar uma venda.")
        return redirect('venda_lista')
    
    if not metodos_envio.exists():
        messages.warning(request, "É necessário cadastrar métodos de envio antes de criar uma venda.")
        return redirect('venda_lista')
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        cliente_nome = request.POST.get('cliente_nome')
        cliente_email = request.POST.get('cliente_email')
        cliente_telefone = request.POST.get('cliente_telefone')
        forma_pagamento_id = request.POST.get('forma_pagamento')
        metodo_envio_id = request.POST.get('metodo_envio')
        
        # Valores financeiros da venda
        subtotal = Decimal(request.POST.get('subtotal', '0'))
        desconto_percentual = Decimal(request.POST.get('desconto_percentual', '0'))
        desconto_valor = Decimal(request.POST.get('desconto_valor', '0'))
        valor_frete = Decimal(request.POST.get('valor_frete', '0'))
        valor_total = Decimal(request.POST.get('valor_total', '0'))
        
        # Validações básicas
        if not forma_pagamento_id or not metodo_envio_id:
            messages.error(request, "Forma de pagamento e método de envio são obrigatórios.")
            return redirect('venda_nova')
        
        # Verificar se tem cliente informado (cadastrado ou nome manual)
        if not cliente_id and not cliente_nome:
            messages.error(request, "Por favor, selecione um cliente cadastrado ou informe pelo menos o nome do cliente.")
            return redirect('venda_nova')
        
        # Obter os objetos relacionados
        forma_pagamento = get_object_or_404(FormaPagamento, id=forma_pagamento_id)
        metodo_envio = get_object_or_404(MetodoEnvio, id=metodo_envio_id)
        cliente_cadastrado = None
        
        if cliente_id:
            cliente_cadastrado = get_object_or_404(ClienteEmpresa, id=cliente_id, usuario_proprietario=request.user)
        elif not cliente_nome.strip():
            # Verificação adicional para garantir que o nome do cliente não esteja vazio ou apenas com espaços
            messages.error(request, "O nome do cliente é obrigatório quando não há cliente cadastrado selecionado.")
            return redirect('venda_nova')
        
        # Obter endereço de entrega
        logradouro_entrega = request.POST.get('logradouro_entrega')
        numero_entrega = request.POST.get('numero_entrega')
        cidade_entrega = request.POST.get('cidade_entrega')
        estado_entrega = request.POST.get('estado_entrega')
        cep_entrega = request.POST.get('cep_entrega')
        
        # Verificar se é envio presencial
        is_presencial = 'Presencial' in metodo_envio.nome
        
        # Se não for presencial, validar campos de endereço
        if not is_presencial and (not logradouro_entrega or not numero_entrega or not cidade_entrega or not estado_entrega or not cep_entrega):
            messages.error(request, "Para entregas não presenciais, os dados de endereço são obrigatórios.")
            return redirect('venda_nova')
        
        # Verificar se existem produtos na venda
        tem_produtos = False
        for key in request.POST:
            if key.startswith('produtos[') and key.endswith('][id]'):
                tem_produtos = True
                break
        
        if not tem_produtos:
            messages.error(request, "Adicione pelo menos um produto à venda.")
            return redirect('venda_nova')
        
        # Criar a venda e adicionar produtos
        try:
            with transaction.atomic():
                venda = Venda.objects.create(
                    usuario_vendedor=request.user,
                    cliente_cadastrado=cliente_cadastrado,
                    cliente_nome=cliente_nome if not cliente_cadastrado else None,
                    cliente_email=cliente_email if not cliente_cadastrado else None,
                    cliente_telefone=cliente_telefone if not cliente_cadastrado else None,
                    forma_pagamento=forma_pagamento,
                    metodo_envio=metodo_envio,
                    valor_frete=valor_frete,
                    endereco_entrega=logradouro_entrega,
                    numero_entrega=numero_entrega,
                    cidade_entrega=cidade_entrega,
                    estado_entrega=estado_entrega,
                    cep_entrega=cep_entrega,
                    status=StatusVenda.RASCUNHO,
                    observacoes=request.POST.get('observacoes'),
                    subtotal=subtotal,
                    desconto_percentual=desconto_percentual,
                    desconto_valor=desconto_valor,
                    valor_total=valor_total
                )
                
                # Processar os produtos adicionados
                produtos_adicionados = {}
                for key in request.POST:
                    if key.startswith('produtos[') and key.endswith('][id]'):
                        # Extrair o índice do produto
                        index = key.split('[')[1].split(']')[0]
                        produto_id = request.POST.get(f'produtos[{index}][id]')
                        quantidade = int(request.POST.get(f'produtos[{index}][quantidade]', 1))
                        valor_unitario = Decimal(request.POST.get(f'produtos[{index}][valor_unitario]', 0))
                        
                        # Adicionar à lista temporária
                        if produto_id not in produtos_adicionados:
                            produtos_adicionados[produto_id] = {
                                'quantidade': quantidade,
                                'valor_unitario': valor_unitario
                            }
                        else:
                            # Se o produto já foi adicionado, somar a quantidade
                            produtos_adicionados[produto_id]['quantidade'] += quantidade
                
                # Adicionar os produtos à venda
                for produto_id, dados in produtos_adicionados.items():
                    produto = get_object_or_404(ProdutoEmpresa, id=produto_id, usuario_proprietario=request.user)
                    
                    # Verificar estoque
                    if produto.estoque < dados['quantidade']:
                        # Rollback automático devido ao contexto de transaction.atomic()
                        messages.error(request, f"Estoque insuficiente para o produto {produto.nome}. Disponível: {produto.estoque}")
                        raise ValidationError(f"Estoque insuficiente para o produto {produto.nome}")
                    
                    # Criar o item da venda
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=dados['quantidade'],
                        valor_unitario=dados['valor_unitario']
                    )
                    
                    # Atualizar estoque do produto
                    produto.estoque -= dados['quantidade']
                    produto.save()
                
                # Atualizar valores da venda (embora já tenhamos definido os valores, isso garante consistência)
                venda.atualizar_valores()
                
                messages.success(request, f"Venda #{venda.id} criada com sucesso com {len(produtos_adicionados)} produtos!")
                return redirect('venda_detalhe', id=venda.id)
        
        except ValidationError as e:
            # Mensagens de erro já foram definidas acima
            return redirect('venda_nova')
        except Exception as e:
            messages.error(request, f"Erro ao criar a venda: {str(e)}")
            return redirect('venda_nova')
    
    context = {
        'formas_pagamento': formas_pagamento,
        'metodos_envio': metodos_envio,
        'clientes': clientes,
        'produtos': produtos,
        'titulo': 'Nova Venda',
        'subtitulo': 'Cadastre uma nova venda',
        'botao': 'Criar Venda'
    }
    
    return render(request, 'vendas/venda_form.html', context)

@login_required
def obter_dados_cliente(request, cliente_id):
    """
    Retorna os dados do cliente em formato JSON para preenchimento via AJAX
    Inclui todos os endereços ativos do cliente
    """
    try:
        cliente = ClienteEmpresa.objects.get(id=cliente_id, usuario_proprietario=request.user)
        # Buscar todos os endereços ativos do cliente
        enderecos = Endereco.objects.filter(cliente=cliente, ativo=True).order_by('tipo', '-data_cadastro')
        
        dados = {
            'nome': cliente.nome,
            'email': cliente.email,
            'telefone': cliente.telefone,
            'success': True,
            'enderecos': []
        }
        
        if enderecos.exists():
            for endereco in enderecos:
                dados['enderecos'].append({
                    'id': endereco.id,
                    'tipo': endereco.tipo,
                    'nome': endereco.nome or f'Endereço {endereco.get_tipo_display()}',
                    'logradouro': endereco.logradouro or '',
                    'numero': endereco.numero or '',
                    'complemento': endereco.complemento or '',
                    'bairro': endereco.bairro or '',
                    'cidade': endereco.cidade or '',
                    'estado': endereco.estado or '',
                    'cep': endereco.cep or '',
                    'endereco_completo': endereco.endereco_completo
                })
        else:
            dados['enderecos'].append({
                'id': 'nenhum',
                'tipo': 'nenhum',
                'nome': 'Nenhum endereço cadastrado',
                'logradouro': '',
                'numero': '',
                'complemento': '',
                'bairro': '',
                'cidade': '',
                'estado': '',
                'cep': '',
                'endereco_completo': ''
            })
        
        return JsonResponse(dados)
    except ClienteEmpresa.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente não encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def venda_editar(request, id):
    """
    Edita uma venda existente
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    # Se a venda já foi finalizada (não é mais rascunho), redireciona para detalhes
    if venda.status != StatusVenda.RASCUNHO:
        messages.info(request, f"A venda #{venda.id} já foi finalizada e não pode ser editada.")
        return redirect('venda_detalhe', id=venda.id)
    
    # Obter produtos do cliente para adicionar à venda
    produtos = ProdutoEmpresa.objects.filter(usuario_proprietario=request.user, ativo=True)
    
    # Processar adição de item à venda
    if request.method == 'POST' and 'adicionar_item' in request.POST:
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))
        
        try:
            produto = get_object_or_404(ProdutoEmpresa, id=produto_id, usuario_proprietario=request.user)
            
            # Verificar se tem estoque suficiente
            if produto.estoque < quantidade:
                messages.error(request, f"Estoque insuficiente para o produto {produto.nome}. Disponível: {produto.estoque}")
                return redirect('venda_editar', id=venda.id)
            
            # Verificar se o produto já está na venda
            item_existente = venda.itens.filter(produto=produto).first()
            if item_existente:
                # Atualizar quantidade do item existente
                nova_quantidade = item_existente.quantidade + quantidade
                if produto.estoque < nova_quantidade:
                    messages.error(request, f"Estoque insuficiente para o produto {produto.nome}. Disponível: {produto.estoque}")
                    return redirect('venda_editar', id=venda.id)
                
                item_existente.quantidade = nova_quantidade
                item_existente.save()
                messages.success(request, f"Quantidade do produto {produto.nome} atualizada para {nova_quantidade}.")
            else:
                # Criar novo item
                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    valor_unitario=produto.preco
                )
                messages.success(request, f"Produto {produto.nome} adicionado à venda.")
            
            # Atualizar os valores da venda
            venda.atualizar_valores()
            
            return redirect('venda_editar', id=venda.id)
        except Exception as e:
            messages.error(request, f"Erro ao adicionar item: {str(e)}")
    
    # Processar desconto
    if request.method == 'POST' and 'aplicar_desconto' in request.POST:
        desconto_percentual = Decimal(request.POST.get('desconto_percentual', 0))
        venda.desconto_percentual = desconto_percentual
        venda.atualizar_valores()
        messages.success(request, f"Desconto de {desconto_percentual}% aplicado com sucesso.")
        return redirect('venda_editar', id=venda.id)
    
    # Processar finalização da venda
    if request.method == 'POST' and 'finalizar_venda' in request.POST:
        if venda.itens.count() == 0:
            messages.error(request, "Não é possível finalizar uma venda sem itens.")
            return redirect('venda_editar', id=venda.id)
        
        venda.status = StatusVenda.PENDENTE
        venda.save()
        messages.success(request, f"Venda #{venda.id} finalizada com sucesso!")
        return redirect('venda_detalhe', id=venda.id)
    
    context = {
        'venda': venda,
        'itens': venda.itens.all(),
        'produtos': produtos,
        'titulo': f'Editar Venda #{venda.id}',
        'subtitulo': 'Adicione produtos ou finalize a venda'
    }
    
    return render(request, 'vendas/venda_editar.html', context)

@login_required
def venda_item_remover(request, venda_id, item_id):
    """
    Remove um item da venda
    """
    venda = get_object_or_404(Venda, id=venda_id, usuario_vendedor=request.user)
    
    # Se a venda já foi finalizada, não permite remover itens
    if venda.status != StatusVenda.RASCUNHO:
        messages.error(request, "Não é possível remover itens de uma venda finalizada.")
        return redirect('venda_detalhe', id=venda_id)
    
    item = get_object_or_404(ItemVenda, id=item_id, venda=venda)
    produto_nome = item.produto.nome
    
    item.delete()
    venda.atualizar_valores()
    
    messages.success(request, f"Item {produto_nome} removido da venda.")
    return redirect('venda_editar', id=venda_id)

@login_required
def venda_cancelar(request, id):
    """
    Cancela uma venda
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    if request.method == 'POST':
        if venda.cancelar():
            messages.success(request, f"Venda #{venda.id} cancelada com sucesso.")
        else:
            messages.error(request, "Não é possível cancelar esta venda devido ao seu status atual.")
        
        return redirect('venda_lista')
    
    context = {
        'venda': venda,
        'titulo': f'Cancelar Venda #{venda.id}',
        'subtitulo': 'Tem certeza que deseja cancelar esta venda?'
    }
    
    return render(request, 'vendas/venda_cancelar.html', context)

@login_required
def venda_confirmar_pagamento(request, id):
    """
    Confirma o pagamento de uma venda
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    if request.method == 'POST':
        if venda.status == StatusVenda.PENDENTE:
            venda.status = StatusVenda.PAGO
            venda.save()
            messages.success(request, f"Pagamento da venda #{venda.id} confirmado com sucesso.")
        else:
            messages.error(request, "Não é possível confirmar o pagamento desta venda devido ao seu status atual.")
        
        return redirect('venda_lista')
    
    context = {
        'venda': venda,
        'titulo': f'Confirmar Pagamento da Venda #{venda.id}',
        'subtitulo': 'Tem certeza que deseja confirmar o pagamento desta venda?'
    }
    
    return render(request, 'vendas/venda_confirmar_pagamento.html', context)

@login_required
def venda_marcar_enviado(request, id):
    """
    Marca uma venda como enviada
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    if request.method == 'POST':
        codigo_rastreamento = request.POST.get('codigo_rastreamento')
        
        if venda.status == StatusVenda.PAGO:
            venda.status = StatusVenda.ENVIADO
            venda.codigo_rastreamento = codigo_rastreamento
            venda.save()
            messages.success(request, f"Venda #{venda.id} marcada como enviada.")
        else:
            messages.error(request, "Não é possível marcar esta venda como enviada devido ao seu status atual.")
        
        return redirect('venda_lista')
    
    context = {
        'venda': venda,
        'titulo': f'Marcar Venda #{venda.id} como Enviada',
        'subtitulo': 'Informe o código de rastreamento (opcional)'
    }
    
    return render(request, 'vendas/venda_marcar_enviado.html', context)

@login_required
def venda_marcar_entregue(request, id):
    """
    Marca uma venda como entregue
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    if request.method == 'POST':
        if venda.status == StatusVenda.ENVIADO:
            venda.status = StatusVenda.ENTREGUE
            venda.save()
            messages.success(request, f"Venda #{venda.id} marcada como entregue.")
        else:
            messages.error(request, "Não é possível marcar esta venda como entregue devido ao seu status atual.")
        
        return redirect('venda_lista')
    
    context = {
        'venda': venda,
        'titulo': f'Marcar Venda #{venda.id} como Entregue',
        'subtitulo': 'Tem certeza que deseja marcar esta venda como entregue?'
    }
    
    return render(request, 'vendas/venda_marcar_entregue.html', context)

@login_required
def venda_dashboard(request):
    """
    Painel de controle das vendas
    """
    # Obter estatísticas de vendas
    hoje = timezone.now()
    primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Total de vendas no mês
    vendas_mes = Venda.objects.filter(
        usuario_vendedor=request.user,
        data_venda__gte=primeiro_dia_mes,
        status__in=[StatusVenda.PAGO, StatusVenda.ENVIADO, StatusVenda.ENTREGUE]
    )
    
    # Valor total das vendas do mês
    valor_total_mes = vendas_mes.aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Vendas recentes
    vendas_recentes = Venda.objects.filter(
        usuario_vendedor=request.user
    ).order_by('-data_venda')[:5]
    
    # Produtos mais vendidos
    produtos_mais_vendidos = ItemVenda.objects.filter(
        venda__usuario_vendedor=request.user,
        venda__status__in=[StatusVenda.PAGO, StatusVenda.ENVIADO, StatusVenda.ENTREGUE]
    ).values(
        'produto__nome'
    ).annotate(
        total_quantidade=Sum('quantidade'),
        total_valor=Sum(F('quantidade') * F('valor_unitario'), output_field=DecimalField())
    ).order_by('-total_quantidade')[:5]
    
    context = {
        'titulo': 'Dashboard de Vendas',
        'subtitulo': 'Visão geral das suas vendas',
        'total_vendas_mes': vendas_mes.count(),
        'valor_total_mes': valor_total_mes,
        'vendas_recentes': vendas_recentes,
        'produtos_mais_vendidos': produtos_mais_vendidos,
    }
    
    return render(request, 'vendas/venda_dashboard.html', context)

@login_required
def venda_pdf(request, id):
    """
    Gera um PDF com os detalhes da venda
    """
    venda = get_object_or_404(Venda, id=id)
    
    # Verificar se o usuário tem permissão para ver esta venda
    if venda.usuario_vendedor != request.user and not request.user.is_superuser:
        messages.error(request, 'Você não tem permissão para acessar esta venda.')
        return redirect('venda_lista')
    
    # Criar o buffer para o PDF
    buffer = BytesIO()
    
    # Criar o PDF
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Configurar o título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, f"Venda #{venda.id}")
    
    # Informações da venda
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Data: {venda.data_venda.strftime('%d/%m/%Y %H:%M')}")
    # Obter o nome do cliente de forma adequada
    cliente = venda.cliente_cadastrado.nome if venda.cliente_cadastrado else venda.cliente_nome
    p.drawString(50, 680, f"Cliente: {cliente}")
    p.drawString(50, 660, f"Status: {venda.get_status_display()}")
    
    # Itens da venda
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 620, "Itens da Venda:")
    
    y = 600
    p.setFont("Helvetica", 10)
    for item in venda.itens.all():
        p.drawString(50, y, f"{item.produto.nome} - {item.quantidade}x R$ {item.valor_unitario}")
        y -= 20
    
    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y-20, f"Total: R$ {venda.valor_total}")
    
    # Finalizar o PDF
    p.showPage()
    p.save()
    
    # Obter o conteúdo do buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Criar a resposta
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="venda_{venda.id}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def venda_finalizar(request, id):
    """
    Finaliza uma venda em rascunho, alterando seu status para pendente
    """
    venda = get_object_or_404(Venda, id=id, usuario_vendedor=request.user)
    
    if request.method == 'POST' or request.method == 'GET':  # Aceita tanto GET quanto POST para facilitar chamadas a partir do template
        if venda.status == StatusVenda.RASCUNHO:
            # Verifica se a venda tem itens
            if venda.itens.count() == 0:
                messages.error(request, "Não é possível finalizar uma venda sem itens.")
                return redirect('venda_editar', id=venda.id)
            
            # Atualiza o status da venda
            venda.status = StatusVenda.PENDENTE
            venda.save()
            messages.success(request, f"Venda #{venda.id} finalizada com sucesso!")
        else:
            messages.warning(request, "Esta venda já foi finalizada anteriormente.")
        
        return redirect('venda_detalhe', id=venda.id)
    
    # Se for outro método HTTP, retorna para a página de detalhes
    return redirect('venda_detalhe', id=venda.id)

@login_required
def atualizar_enderecos_cliente(request):
    """
    Endpoint para atualizar os endereços de um cliente via AJAX.
    Trabalha com dados estruturados de endereços, suportando até 3 endereços por cliente.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        # Carregar dados do corpo da requisição JSON
        import json
        dados = json.loads(request.body)
        
        # Validar dados recebidos
        cliente_id = dados.get('cliente_id')
        enderecos_dados = dados.get('enderecos', [])
        
        if not cliente_id:
            return JsonResponse({'success': False, 'message': 'ID do cliente não informado'})
        
        # Para compatibilidade
        endereco_principal = dados.get('endereco_principal')
        endereco_secundario = dados.get('endereco_secundario')
        endereco_adicional = dados.get('endereco_adicional')
            
        # Obter o cliente
        cliente = ClienteEmpresa.objects.get(id=cliente_id, usuario_proprietario=request.user)
        
        # Verificar se temos dados de endereços estruturados ou em formato antigo
        if enderecos_dados:
            # Formato novo: dados estruturados de endereços
            # Verificar limite de endereços (máximo 3)
            if len(enderecos_dados) > 3:
                return JsonResponse({'success': False, 'message': 'Limite de 3 endereços por cliente'})
            
            # Marcar todos os endereços como inativos para ativar apenas os enviados
            Endereco.objects.filter(cliente=cliente).update(ativo=False)
            
            # Processar cada endereço enviado
            enderecos_salvos = []
            tipo_principal_encontrado = False
            
            for endereco_dado in enderecos_dados:
                endereco_id = endereco_dado.get('id')
                tipo = endereco_dado.get('tipo', 'outro')
                
                # Verificar se já existe endereço deste tipo entre os atualizados
                if tipo in [e.tipo for e in enderecos_salvos] and tipo != 'outro':
                    return JsonResponse({
                        'success': False, 
                        'message': f'Múltiplos endereços do tipo "{tipo}" encontrados'
                    })
                
                # Se for tipo principal, marcar que encontramos
                if tipo == 'principal':
                    tipo_principal_encontrado = True
                
                # Verificar se é atualização ou criação
                if endereco_id and endereco_id != 'nenhum':
                    try:
                        endereco = Endereco.objects.get(id=endereco_id, cliente=cliente)
                        endereco.tipo = tipo
                        endereco.nome = endereco_dado.get('nome', '')
                        endereco.logradouro = endereco_dado.get('logradouro', '')
                        endereco.numero = endereco_dado.get('numero', '')
                        endereco.complemento = endereco_dado.get('complemento', '')
                        endereco.bairro = endereco_dado.get('bairro', '')
                        endereco.cidade = endereco_dado.get('cidade', '')
                        endereco.estado = endereco_dado.get('estado', '')
                        endereco.cep = endereco_dado.get('cep', '')
                        endereco.ativo = True
                        endereco.save()
                        enderecos_salvos.append(endereco)
                    except Endereco.DoesNotExist:
                        return JsonResponse({
                            'success': False, 
                            'message': f'Endereço com ID {endereco_id} não encontrado'
                        })
                else:
                    # Criar novo endereço
                    endereco = Endereco(
                        cliente=cliente,
                        tipo=tipo,
                        nome=endereco_dado.get('nome', ''),
                        logradouro=endereco_dado.get('logradouro', ''),
                        numero=endereco_dado.get('numero', ''),
                        complemento=endereco_dado.get('complemento', ''),
                        bairro=endereco_dado.get('bairro', ''),
                        cidade=endereco_dado.get('cidade', ''),
                        estado=endereco_dado.get('estado', ''),
                        cep=endereco_dado.get('cep', ''),
                        ativo=True
                    )
                    endereco.save()
                    enderecos_salvos.append(endereco)
            
            # Verificar se temos pelo menos um endereço principal
            if enderecos_salvos and not tipo_principal_encontrado:
                # Definir o primeiro endereço como principal
                primeiro_endereco = enderecos_salvos[0]
                primeiro_endereco.tipo = 'principal'
                primeiro_endereco.save(update_fields=['tipo'])
                
                # Atualizar os campos de compatibilidade
                cliente.endereco_principal = primeiro_endereco.endereco_completo
                cliente.endereco_cidade = primeiro_endereco.cidade
                cliente.endereco_estado = primeiro_endereco.estado
                cliente.endereco_cep = primeiro_endereco.cep
                cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
            elif tipo_principal_encontrado:
                # Atualizar campos de compatibilidade com o endereço principal
                principal = next((e for e in enderecos_salvos if e.tipo == 'principal'), None)
                if principal:
                    cliente.endereco_principal = principal.endereco_completo
                    cliente.endereco_cidade = principal.cidade
                    cliente.endereco_estado = principal.estado
                    cliente.endereco_cep = principal.cep
                    cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
        else:
            # Formato antigo: strings de endereço (para compatibilidade)
            # Apenas para compatibilidade com código antigo
            cliente.endereco_principal = endereco_principal
            cliente.endereco_secundario = endereco_secundario
            cliente.endereco_adicional = endereco_adicional
            cliente.save(update_fields=['endereco_principal', 'endereco_secundario', 'endereco_adicional'])
            
            # Processa os endereços e atualiza/cria no model Endereco
            tipos_endereco = [
                ('principal', endereco_principal),
                ('secundario', endereco_secundario),
                ('adicional', endereco_adicional)
            ]
            
            for tipo, texto in tipos_endereco:
                if not texto:
                    # Se o endereço foi removido ou está vazio, desativa os existentes
                    Endereco.objects.filter(cliente=cliente, tipo=tipo).update(ativo=False)
                    continue
                    
                # Extrai dados do texto do endereço
                dados_endereco = extrair_dados_endereco(texto)
                if not dados_endereco:
                    continue
                    
                # Tenta encontrar um endereço existente ou cria um novo
                endereco, criado = Endereco.objects.update_or_create(
                    cliente=cliente,
                    tipo=tipo,
                    defaults={
                        'nome': f"Endereço {tipo.capitalize()}",
                        'logradouro': dados_endereco['logradouro'],
                        'numero': dados_endereco['numero'],
                        'complemento': "",  # Não é possível inferir do texto
                        'bairro': dados_endereco['bairro'],
                        'cidade': dados_endereco['cidade'],
                        'estado': dados_endereco['estado'],
                        'cep': dados_endereco['cep'],
                        'ativo': True
                    }
                )
        
        return JsonResponse({
            'success': True,
            'message': 'Endereços atualizados com sucesso'
        })
    
    except ClienteEmpresa.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Cliente não encontrado'})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Dados JSON inválidos'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Função auxiliar para extrair dados do endereço em formato texto
def extrair_dados_endereco(endereco_texto):
    if not endereco_texto:
        return None
            
    # Exemplo padrão: "Rua Exemplo, 123, Bairro, Cidade - UF, 12345-678"
    # Tenta extrair os componentes usando regex
    try:
        import re
        padrao = r"([^,]+),\s*(\d+)(?:,\s*([^,]+))?(?:,\s*([^,-]+))(?:\s*-\s*([A-Z]{2}))?(?:,\s*(\d{5}-\d{3}))?"
        match = re.match(padrao, endereco_texto)
        if match:
            return {
                'logradouro': match.group(1).strip() if match.group(1) else "",
                'numero': match.group(2).strip() if match.group(2) else "",
                'bairro': match.group(3).strip() if match.group(3) else "",
                'cidade': match.group(4).strip() if match.group(4) else "",
                'estado': match.group(5).strip() if match.group(5) else "",
                'cep': match.group(6).strip() if match.group(6) else ""
            }
    except Exception as e:
        print(f"Erro ao extrair dados do endereço: {e}")
        
    # Fallback - retorna apenas o texto como logradouro
    return {
        'logradouro': endereco_texto,
        'numero': '',
        'bairro': '',
        'cidade': '',
        'estado': '',
        'cep': ''
    }

# Não é mais necessária esta função alternativa, já que a função original não tem mais o decorador cliente_required 