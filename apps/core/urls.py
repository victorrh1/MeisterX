from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('logs/', views.audit_logs, name='audit_logs'),
    path('notificacoes/', views.todas_notificacoes, name='todas_notificacoes'),
    path('notificacoes/marcar-lida/<int:notificacao_id>/', views.marcar_lida, name='marcar_lida'),
    path('notificacoes/marcar-todas-lidas/', views.marcar_todas_lidas, name='marcar_todas_lidas'),
] 