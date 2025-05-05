from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil-usuario/', views.perfil_usuario, name='perfil_usuario'),
    path('senha/', views.alterar_senha, name='alterar_senha'),
    path('meus-dados/', views.meus_dados, name='meus_dados'),
    path('meus-produtos/', views.meus_produtos, name='meus_produtos'),
    path('minhas-compras/', views.minhas_compras, name='minhas_compras'),
    path('assinaturas/<int:id>/gerenciar/', views.gerenciar_assinatura, name='gerenciar_assinatura'),
    path('assinaturas/<int:id>/renovar/', views.renovar_assinatura, name='renovar_assinatura'),
    path('assinaturas/<int:id>/cancelar/', views.cancelar_assinatura, name='cancelar_assinatura'),
    path('planos/trial/<int:id>/', views.iniciar_trial, name='iniciar_trial'),
    path('planos/contratar/<int:id>/', views.contratar_plano, name='contratar_plano'),
    path('pagamentos/', views.pagamentos, name='pagamentos'),
    path('contato/', views.contato, name='contato'),
    path('two-factor/verify/', views.two_factor_verify, name='two_factor_verify'),
    path('two-factor/toggle/', views.toggle_two_factor, name='toggle_two_factor'),
    path('pos-login/', views.pos_login_redirect, name='pos_login_redirect'),
    
    # URLs de recuperação de senha
    path('recuperar-senha/', 
        auth_views.PasswordResetView.as_view(
            template_name='usuarios/password_reset_form.html',
            email_template_name='usuarios/password_reset_email.html',
            subject_template_name='usuarios/password_reset_subject.txt',
            success_url='/usuarios/recuperar-senha/enviado/'
        ),
        name='password_reset'
    ),
    path('recuperar-senha/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='usuarios/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('recuperar-senha/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='usuarios/password_reset_confirm.html',
            success_url='/usuarios/recuperar-senha/concluido/'
        ),
        name='password_reset_confirm'
    ),
    path('recuperar-senha/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='usuarios/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    
    # Adicionar uma rota para notificações
    path('notificacoes/', views.notificacoes, name='notificacoes'),
    
    # Adicionar uma rota para o registro de usuários
    path('register/', views.register, name='register'),
    path('admin-usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('aprovar-usuario/<int:user_id>/', views.aprovar_usuario, name='aprovar_usuario'),
    path('rejeitar-usuario/<int:user_id>/', views.rejeitar_usuario, name='rejeitar_usuario'),
] 