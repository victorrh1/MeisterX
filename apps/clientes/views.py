from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.usuarios.decorators import cliente_required
from .models import Cliente, ClienteEmpresa, Endereco
from .forms import ClienteForm, ClienteEmpresaForm, EnderecoFormSet, EnderecoForm
from apps.core.decorators import user_has_permission

@login_required
def lista(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@login_required
def novo(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Novo'})

@login_required
def editar(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'titulo': 'Editar'})

@login_required
@cliente_required
def cliente_empresa_lista(request):
    """
    Lista todos os clientes cadastrados pelo usuário cliente logado
    """
    try:
        clientes = ClienteEmpresa.objects.filter(usuario_proprietario=request.user, ativo=True)
    except Exception as e:
        print(f"Erro ao buscar clientes: {e}")
        clientes = []
        messages.error(request, "Ocorreu um erro ao buscar seus clientes. Entre em contato com o suporte.")
    
    context = {
        'clientes': clientes,
        'titulo': 'Meus Clientes',
        'subtitulo': 'Gerencie os dados dos seus clientes'
    }
    
    return render(request, 'clientes/cliente_empresa_lista.html', context)

@login_required
@cliente_required
def cliente_empresa_novo(request):
    """
    Cadastra um novo cliente para o usuário cliente logado
    Processa o formulário principal e os endereços estruturados
    """
    if request.method == 'POST':
        form = ClienteEmpresaForm(request.POST)
        endereco_formset = EnderecoFormSet(request.POST, instance=ClienteEmpresa(), prefix='endereco')

        if form.is_valid() and endereco_formset.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario_proprietario = request.user
            cliente.save()

            # Vincular o formset ao cliente salvo
            endereco_formset.instance = cliente
            endereco_formset.save()

            # Preencher os campos de compatibilidade
            enderecos_ativos = Endereco.objects.filter(cliente=cliente, ativo=True).order_by('id')
            if enderecos_ativos:
                cliente.endereco_principal = enderecos_ativos[0].endereco_completo
                cliente.endereco_cidade = enderecos_ativos[0].cidade
                cliente.endereco_estado = enderecos_ativos[0].estado
                cliente.endereco_cep = enderecos_ativos[0].cep
                cliente.endereco_secundario = enderecos_ativos[1].endereco_completo if len(enderecos_ativos) > 1 else ''
                cliente.endereco_adicional = enderecos_ativos[2].endereco_completo if len(enderecos_ativos) > 2 else ''
                cliente.save(update_fields=[
                    'endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep',
                    'endereco_secundario', 'endereco_adicional'
                ])

            messages.success(request, "Cliente cadastrado com sucesso!")
            return redirect('cliente_empresa_lista')
        else:
            # Exibir erros do formset
            for form_errors in endereco_formset.errors:
                for field, errors in form_errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo {field}: {error}")
            for error in endereco_formset.non_form_errors():
                messages.error(request, error)
    else:
        form = ClienteEmpresaForm()
        endereco_formset = EnderecoFormSet(instance=ClienteEmpresa(), prefix='endereco')

    context = {
        'form': form,
        'endereco_formset': endereco_formset,
        'titulo': 'Cadastrar Cliente',
        'subtitulo': 'Adicionar um novo cliente',
        'botao': 'Cadastrar'
    }

    return render(request, 'clientes/cliente_empresa_form.html', context)

@login_required
@cliente_required
def cliente_empresa_editar(request, id):
    """
    Edita um cliente existente do usuário cliente logado
    Processa o formulário principal e os endereços estruturados
    """
    cliente = get_object_or_404(ClienteEmpresa, id=id, usuario_proprietario=request.user)

    if request.method == 'POST':
        form = ClienteEmpresaForm(request.POST, instance=cliente)
        endereco_formset = EnderecoFormSet(request.POST, instance=cliente, prefix='endereco')

        if form.is_valid() and endereco_formset.is_valid():
            cliente = form.save()
            endereco_formset.save()

            # Preencher os campos de compatibilidade
            enderecos_ativos = Endereco.objects.filter(cliente=cliente, ativo=True).order_by('id')
            if enderecos_ativos:
                cliente.endereco_principal = enderecos_ativos[0].endereco_completo
                cliente.endereco_cidade = enderecos_ativos[0].cidade
                cliente.endereco_estado = enderecos_ativos[0].estado
                cliente.endereco_cep = enderecos_ativos[0].cep
                cliente.endereco_secundario = enderecos_ativos[1].endereco_completo if len(enderecos_ativos) > 1 else ''
                cliente.endereco_adicional = enderecos_ativos[2].endereco_completo if len(enderecos_ativos) > 2 else ''
                cliente.save(update_fields=[
                    'endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep',
                    'endereco_secundario', 'endereco_adicional'
                ])

            messages.success(request, "Cliente atualizado com sucesso!")
            return redirect('cliente_empresa_lista')
        else:
            # Exibir erros do formset
            for form_errors in endereco_formset.errors:
                for field, errors in form_errors.items():
                    for error in errors:
                        messages.error(request, f"Erro no campo {field}: {error}")
            for error in endereco_formset.non_form_errors():
                messages.error(request, error)
    else:
        form = ClienteEmpresaForm(instance=cliente)
        endereco_formset = EnderecoFormSet(instance=cliente, prefix='endereco')

    context = {
        'form': form,
        'endereco_formset': endereco_formset,
        'titulo': 'Editar Cliente',
        'subtitulo': f'Editando {cliente.nome}',
        'botao': 'Atualizar'
    }

    return render(request, 'clientes/cliente_empresa_form.html', context)

@login_required
@cliente_required
def cliente_empresa_detalhe(request, id):
    """
    Exibe os detalhes de um cliente da empresa específico
    """
    cliente = get_object_or_404(ClienteEmpresa, id=id, usuario_proprietario=request.user)
    
    # Verificar se há vendas relacionadas a este cliente
    vendas = []
    try:
        from apps.vendas.models import Venda
        vendas = Venda.objects.filter(cliente_cadastrado=cliente)
    except:
        # Pode falhar se o app vendas não estiver disponível
        pass
    
    context = {
        'cliente': cliente,
        'titulo': f'Cliente: {cliente.nome}',
        'subtitulo': 'Detalhes do cliente',
        'vendas': vendas
    }
    
    return render(request, 'clientes/cliente_empresa_detalhe.html', context)

@login_required
@cliente_required
def cliente_empresa_excluir(request, id):
    """
    Exclui (marca como inativo) um cliente do usuário cliente logado
    """
    cliente = get_object_or_404(ClienteEmpresa, id=id, usuario_proprietario=request.user)
    
    if request.method == 'POST':
        cliente.ativo = False
        cliente.save()
        messages.success(request, "Cliente excluído com sucesso!")
        return redirect('cliente_empresa_lista')
    
    context = {
        'cliente': cliente,
        'titulo': 'Confirmar Exclusão',
        'subtitulo': f'Tem certeza que deseja excluir o cliente {cliente.nome}?'
    }
    
    return render(request, 'clientes/cliente_empresa_excluir.html', context)

@login_required
def detalhe(request, id):
    """
    Exibe os detalhes de um cliente específico
    """
    cliente = get_object_or_404(Cliente, id=id)
    return render(request, 'clientes/detalhe.html', {
        'cliente': cliente,
        'titulo': f'Cliente: {cliente.nome}',
        'subtitulo': 'Detalhes do cliente'
    })

@login_required
@cliente_required
def cliente_cadastrar_rapido(request):
    """
    Cadastra rapidamente um cliente a partir de uma venda
    """
    # Verificar se está vinculado a uma venda
    venda_id = request.GET.get('venda')
    venda = None
    initial_data = {}
    
    if venda_id:
        try:
            from apps.vendas.models import Venda
            venda = Venda.objects.get(id=venda_id, usuario_vendedor=request.user)
            
            # Preencher dados iniciais do formulário com os dados da venda
            initial_data = {
                'nome': venda.cliente_nome,
                'email': venda.cliente_email,
                'telefone': venda.cliente_telefone,
                'observacoes': f"Cliente cadastrado a partir da venda #{venda.id}"
            }
        except Exception as e:
            print(f"Erro ao buscar venda: {e}")
            messages.error(request, "Não foi possível carregar os dados da venda especificada.")
    
    if request.method == 'POST':
        form = ClienteEmpresaForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.usuario_proprietario = request.user
            cliente.save()
            
            # Atualizar a venda com o cliente cadastrado, se houver uma venda
            if venda:
                venda.cliente_cadastrado = cliente
                venda.save()
            
            messages.success(request, "Cliente cadastrado com sucesso!")
            
            # Redirecionar para a venda se veio de uma venda, ou para a lista de clientes
            if venda:
                return redirect('venda_detalhe', id=venda.id)
            return redirect('cliente_empresa_lista')
    else:
        form = ClienteEmpresaForm(initial=initial_data)
    
    context = {
        'form': form,
        'titulo': 'Cadastro Rápido de Cliente',
        'subtitulo': 'Adicionar um novo cliente a partir da venda',
        'botao': 'Cadastrar',
        'venda': venda
    }
    
    return render(request, 'clientes/cliente_empresa_form.html', context)

@login_required
@cliente_required
def gerenciar_enderecos(request, cliente_id):
    """
    Endpoint para adicionar/editar/remover endereços via AJAX
    """
    cliente = get_object_or_404(ClienteEmpresa, id=cliente_id, usuario_proprietario=request.user)
    
    if request.method == 'POST':
        # Implementação para AJAX
        try:
            import json
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'add':
                # Adicionar novo endereço
                if Endereco.objects.filter(cliente=cliente, ativo=True).count() >= 3:
                    return JsonResponse({'success': False, 'message': 'Limite de 3 endereços atingido'})
                
                endereco = Endereco(
                    cliente=cliente,
                    tipo=data.get('tipo', 'outro'),
                    nome=data.get('nome', ''),
                    logradouro=data.get('logradouro', ''),
                    numero=data.get('numero', ''),
                    complemento=data.get('complemento', ''),
                    bairro=data.get('bairro', ''),
                    cidade=data.get('cidade', ''),
                    estado=data.get('estado', ''),
                    cep=data.get('cep', ''),
                    ativo=True
                )
                endereco.save()
                
                # Se for endereço principal, atualizar os campos de compatibilidade
                if endereco.tipo == 'principal':
                    cliente.endereco_principal = endereco.endereco_completo
                    cliente.endereco_cidade = endereco.cidade
                    cliente.endereco_estado = endereco.estado
                    cliente.endereco_cep = endereco.cep
                    cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Endereço adicionado com sucesso',
                    'endereco': {
                        'id': endereco.id,
                        'tipo': endereco.tipo,
                        'nome': endereco.nome,
                        'endereco_completo': endereco.endereco_completo
                    }
                })
                
            elif action == 'edit':
                # Editar endereço existente
                endereco_id = data.get('id')
                endereco = get_object_or_404(Endereco, id=endereco_id, cliente=cliente)
                
                endereco.tipo = data.get('tipo', endereco.tipo)
                endereco.nome = data.get('nome', endereco.nome)
                endereco.logradouro = data.get('logradouro', endereco.logradouro)
                endereco.numero = data.get('numero', endereco.numero)
                endereco.complemento = data.get('complemento', endereco.complemento)
                endereco.bairro = data.get('bairro', endereco.bairro)
                endereco.cidade = data.get('cidade', endereco.cidade)
                endereco.estado = data.get('estado', endereco.estado)
                endereco.cep = data.get('cep', endereco.cep)
                endereco.save()
                
                # Se for endereço principal, atualizar os campos de compatibilidade
                if endereco.tipo == 'principal':
                    cliente.endereco_principal = endereco.endereco_completo
                    cliente.endereco_cidade = endereco.cidade
                    cliente.endereco_estado = endereco.estado
                    cliente.endereco_cep = endereco.cep
                    cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Endereço atualizado com sucesso',
                    'endereco': {
                        'id': endereco.id,
                        'tipo': endereco.tipo,
                        'nome': endereco.nome,
                        'endereco_completo': endereco.endereco_completo
                    }
                })
                
            elif action == 'delete':
                # Remover endereço (marcar como inativo)
                endereco_id = data.get('id')
                endereco = get_object_or_404(Endereco, id=endereco_id, cliente=cliente)
                endereco.ativo = False
                endereco.save(update_fields=['ativo'])
                
                # Se era o endereço principal, tentar encontrar outro para ser o principal
                if endereco.tipo == 'principal':
                    # Limpar os campos de compatibilidade
                    cliente.endereco_principal = ''
                    cliente.endereco_cidade = ''
                    cliente.endereco_estado = ''
                    cliente.endereco_cep = ''
                    
                    # Buscar outro endereço ativo para ser o principal
                    outro_endereco = Endereco.objects.filter(cliente=cliente, ativo=True).first()
                    if outro_endereco:
                        outro_endereco.tipo = 'principal'
                        outro_endereco.save(update_fields=['tipo'])
                        
                        cliente.endereco_principal = outro_endereco.endereco_completo
                        cliente.endereco_cidade = outro_endereco.cidade
                        cliente.endereco_estado = outro_endereco.estado
                        cliente.endereco_cep = outro_endereco.cep
                    
                    cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
                
                return JsonResponse({'success': True, 'message': 'Endereço removido com sucesso'})
                
            else:
                return JsonResponse({'success': False, 'message': 'Ação inválida'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # Listar endereços
    enderecos = Endereco.objects.filter(cliente=cliente, ativo=True)
    enderecos_data = [{
        'id': endereco.id,
        'tipo': endereco.tipo,
        'nome': endereco.nome,
        'logradouro': endereco.logradouro,
        'numero': endereco.numero,
        'complemento': endereco.complemento,
        'bairro': endereco.bairro,
        'cidade': endereco.cidade,
        'estado': endereco.estado,
        'cep': endereco.cep,
        'endereco_completo': endereco.endereco_completo
    } for endereco in enderecos]
    
    return JsonResponse({'success': True, 'enderecos': enderecos_data})

@login_required
def deletar(request, id):
    """
    Exclui (marca como inativo) um cliente
    """
    cliente = get_object_or_404(Cliente, id=id)
    
    if request.method == 'POST':
        cliente.ativo = False
        cliente.save()
        messages.success(request, "Cliente excluído com sucesso!")
        return redirect('clientes_lista')
    
    context = {
        'cliente': cliente,
        'titulo': 'Confirmar Exclusão',
        'subtitulo': f'Tem certeza que deseja excluir o cliente {cliente.nome}?'
    }
    
    return render(request, 'clientes/cliente_excluir.html', context)

@login_required
@cliente_required
def adicionar_endereco(request, cliente_id):
    """View para adicionar um novo endereço a um cliente existente."""
    cliente = get_object_or_404(ClienteEmpresa, id=cliente_id, usuario_proprietario=request.user)
    
    # Verificar se o cliente já tem 3 endereços
    enderecos_existentes = Endereco.objects.filter(cliente=cliente, ativo=True).count()
    if enderecos_existentes >= 3:
        messages.error(request, "Limite de 3 endereços por cliente atingido.")
        return redirect('cliente_empresa_editar', id=cliente.id)
    
    # Verificar se já existe um endereço principal
    tem_principal = Endereco.objects.filter(cliente=cliente, tipo='principal', ativo=True).exists()
    
    # Se não tiver endereço ainda, este será o principal
    eh_primeiro = enderecos_existentes == 0
    
    if request.method == 'POST':
        form = EnderecoForm(request.POST)
        if form.is_valid():
            endereco = form.save(commit=False)
            endereco.cliente = cliente
            
            # Verificar se deve forçar como principal
            if eh_primeiro:
                endereco.tipo = 'principal'
            # Verificar se não está tentando criar outro endereço principal
            elif endereco.tipo == 'principal' and tem_principal:
                messages.error(request, "Já existe um endereço principal. Edite o endereço existente ou escolha outro tipo.")
                return render(request, 'clientes/endereco_form.html', {
                    'form': form,
                    'cliente': cliente,
                    'titulo': 'Adicionar Endereço',
                    'botao': 'Adicionar',
                    'modo': 'adicionar'
                })
            
            endereco.save()
            
            # Se for endereço principal, atualizar campos de compatibilidade
            if endereco.tipo == 'principal':
                cliente.endereco_principal = endereco.endereco_completo
                cliente.endereco_cidade = endereco.cidade
                cliente.endereco_estado = endereco.estado
                cliente.endereco_cep = endereco.cep
                cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
            
            messages.success(request, "Endereço adicionado com sucesso.")
            return redirect('cliente_empresa_editar', id=cliente.id)
    else:
        # Se for o primeiro endereço, pré-selecionar como principal
        initial = {'tipo': 'principal'} if eh_primeiro else {}
        form = EnderecoForm(initial=initial)
        
        # Se já existir principal, desabilitar a opção no form
        if tem_principal:
            form.fields['tipo'].choices = [choice for choice in form.fields['tipo'].choices if choice[0] != 'principal']
    
    return render(request, 'clientes/endereco_form.html', {
        'form': form,
        'cliente': cliente,
        'titulo': 'Adicionar Endereço',
        'botao': 'Adicionar',
        'modo': 'adicionar',
        'is_principal': eh_primeiro  # Passar variável para o template
    })

@login_required
@cliente_required
def editar_endereco(request, endereco_id):
    """View para editar um endereço existente."""
    endereco = get_object_or_404(Endereco, id=endereco_id)
    cliente = endereco.cliente
    
    # Verificar se o usuário é proprietário do cliente
    if cliente.usuario_proprietario != request.user:
        messages.error(request, "Você não tem permissão para editar este endereço.")
        return redirect('dashboard')
    
    # Verificar se havia endereço principal para controle de alteração
    era_principal = endereco.tipo == 'principal'
    
    if request.method == 'POST':
        form = EnderecoForm(request.POST, instance=endereco)
        if form.is_valid():
            endereco = form.save()
            
            # Se for ou se tornou endereço principal, atualizar campos de compatibilidade
            if endereco.tipo == 'principal':
                cliente.endereco_principal = endereco.endereco_completo
                cliente.endereco_cidade = endereco.cidade
                cliente.endereco_estado = endereco.estado
                cliente.endereco_cep = endereco.cep
                cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
            # Se deixou de ser principal, limpar campos de compatibilidade e procurar outro para ser principal
            elif era_principal and endereco.tipo != 'principal':
                # Limpar os campos de compatibilidade
                cliente.endereco_principal = ''
                cliente.endereco_cidade = ''
                cliente.endereco_estado = ''
                cliente.endereco_cep = ''
                
                # Buscar outro endereço para ser o principal
                outro_endereco = Endereco.objects.filter(cliente=cliente, ativo=True).exclude(id=endereco.id).first()
                if outro_endereco:
                    outro_endereco.tipo = 'principal'
                    outro_endereco.save(update_fields=['tipo'])
                    
                    cliente.endereco_principal = outro_endereco.endereco_completo
                    cliente.endereco_cidade = outro_endereco.cidade
                    cliente.endereco_estado = outro_endereco.estado
                    cliente.endereco_cep = outro_endereco.cep
                
                cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
            
            messages.success(request, "Endereço atualizado com sucesso.")
            return redirect('cliente_empresa_editar', id=cliente.id)
    else:
        form = EnderecoForm(instance=endereco)
        
        # Se for o único endereço, travar como principal
        if Endereco.objects.filter(cliente=cliente, ativo=True).count() == 1 and endereco.tipo == 'principal':
            form.fields['tipo'].widget.attrs['disabled'] = True
            form.fields['tipo'].widget.attrs['readonly'] = True
            form.fields['tipo'].initial = 'principal'
    
    return render(request, 'clientes/endereco_form.html', {
        'form': form,
        'cliente': cliente,
        'endereco': endereco,
        'titulo': 'Editar Endereço',
        'botao': 'Salvar',
        'modo': 'editar',
        'is_principal': endereco.tipo == 'principal' and Endereco.objects.filter(cliente=cliente, ativo=True).count() == 1
    })

@login_required
@cliente_required
def remover_endereco(request, endereco_id):
    """View para confirmar e remover um endereço."""
    endereco = get_object_or_404(Endereco, id=endereco_id)
    cliente = endereco.cliente
    
    # Verificar se o usuário é proprietário do cliente
    if cliente.usuario_proprietario != request.user:
        messages.error(request, "Você não tem permissão para remover este endereço.")
        return redirect('dashboard')
    
    # Não permitir remover o endereço principal (o primeiro endereço)
    enderecos = Endereco.objects.filter(cliente=cliente, ativo=True).order_by('id')
    if not enderecos.exists():
        messages.error(request, "Não há endereços ativos para remover.")
        return redirect('cliente_empresa_editar', id=cliente.id)
    
    if endereco.tipo == 'principal':
        messages.error(request, "Não é possível remover o endereço principal.")
        return redirect('cliente_empresa_editar', id=cliente.id)
    
    if request.method == 'POST':
        # Em vez de excluir, marcar como inativo (soft delete)
        endereco.ativo = False
        endereco.save(update_fields=['ativo'])
        
        # Atualizar campos de compatibilidade se necessário
        if endereco.tipo == 'principal':
            # Limpar os campos de compatibilidade
            cliente.endereco_principal = ''
            cliente.endereco_cidade = ''
            cliente.endereco_estado = ''
            cliente.endereco_cep = ''
            
            # Buscar outro endereço ativo para ser o principal
            outro_endereco = Endereco.objects.filter(cliente=cliente, ativo=True).first()
            if outro_endereco:
                outro_endereco.tipo = 'principal'
                outro_endereco.save(update_fields=['tipo'])
                
                cliente.endereco_principal = outro_endereco.endereco_completo
                cliente.endereco_cidade = outro_endereco.cidade
                cliente.endereco_estado = outro_endereco.estado
                cliente.endereco_cep = outro_endereco.cep
            
            cliente.save(update_fields=['endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep'])
        
        messages.success(request, "Endereço removido com sucesso.")
        return redirect('cliente_empresa_editar', id=cliente.id)
    
    return render(request, 'clientes/endereco_confirmar_remocao.html', {
        'endereco': endereco,
        'cliente': cliente
    })