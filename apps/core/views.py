from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from usuarios.decorators import admin_required
from .models import AuditLog, Notification

# Create your views here.

@login_required
@admin_required
def audit_logs(request):
    # Filtros
    filtros = {}
    
    acao = request.GET.get('acao')
    if acao:
        filtros['acao'] = acao
        
    usuario = request.GET.get('usuario')
    if usuario:
        filtros['usuario__username__icontains'] = usuario
        
    data_inicio = request.GET.get('data_inicio')
    if data_inicio:
        filtros['data_hora__date__gte'] = data_inicio
        
    data_fim = request.GET.get('data_fim')
    if data_fim:
        filtros['data_hora__date__lte'] = data_fim
        
    # Query
    logs = AuditLog.objects.filter(**filtros)
    
    # Paginação
    paginator = Paginator(logs, 20)
    page = request.GET.get('page')
    logs_paginados = paginator.get_page(page)
    
    context = {
        'logs': logs_paginados,
        'acoes': AuditLog.ACOES,
        'filtros': request.GET
    }
    
    return render(request, 'core/audit_logs.html', context)

@login_required
def todas_notificacoes(request):
    """View para listar todas as notificações do usuário"""
    notificacoes = request.user.notificacoes.all()
    
    # Paginação
    paginator = Paginator(notificacoes, 20)
    page = request.GET.get('page')
    notificacoes_paginadas = paginator.get_page(page)
    
    context = {
        'notificacoes': notificacoes_paginadas
    }
    
    return render(request, 'core/todas_notificacoes.html', context)

@login_required
def marcar_lida(request, notificacao_id):
    """View para marcar uma notificação como lida"""
    notificacao = get_object_or_404(Notification, id=notificacao_id, usuario=request.user)
    notificacao.lida = True
    notificacao.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    messages.success(request, 'Notificação marcada como lida.')
    return redirect('core:todas_notificacoes')

@login_required
def marcar_todas_lidas(request):
    """View para marcar todas as notificações do usuário como lidas"""
    request.user.notificacoes.filter(lida=False).update(lida=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
        
    messages.success(request, 'Todas as notificações foram marcadas como lidas.')
    return redirect('core:todas_notificacoes')
