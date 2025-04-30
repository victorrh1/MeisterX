from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario, PerfilUsuario, TwoFactorCode
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import Group

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'grupo', 'date_joined')
    list_filter = ('is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name', 'email', 'cpf')}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas Importantes'), {'fields': ('last_login', 'date_joined')}),
        (_('Segurança'), {'fields': ('two_factor_enabled',)}),
    )

    actions = ['make_admin', 'make_equipe', 'make_cliente']

    def grupo(self, obj):
        return obj.grupo
    
    def make_admin(self, request, queryset):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        for user in queryset:
            user.groups.add(admin_group)
        self.message_user(request, f'{queryset.count()} usuário(s) adicionado(s) ao grupo Admin.')
    make_admin.short_description = 'Adicionar ao grupo Admin'
    
    def make_equipe(self, request, queryset):
        equipe_group, _ = Group.objects.get_or_create(name='Equipe')
        for user in queryset:
            user.groups.add(equipe_group)
        self.message_user(request, f'{queryset.count()} usuário(s) adicionado(s) ao grupo Equipe.')
    make_equipe.short_description = 'Adicionar ao grupo Equipe'
    
    def make_cliente(self, request, queryset):
        cliente_group, _ = Group.objects.get_or_create(name='Cliente')
        for user in queryset:
            user.groups.add(cliente_group)
        self.message_user(request, f'{queryset.count()} usuário(s) adicionado(s) ao grupo Cliente.')
    make_cliente.short_description = 'Adicionar ao grupo Cliente'

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_approved', 'pending_approval', 'registration_date', 'approval_date')
    list_filter = ('is_approved', 'pending_approval', 'registration_date')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-registration_date',)
    
    actions = ['approve_users']
    
    def approve_users(self, request, queryset):
        cliente_group, _ = Group.objects.get_or_create(name='Cliente')
        count = 0
        
        for perfil in queryset.filter(pending_approval=True, is_approved=False):
            perfil.is_approved = True
            perfil.pending_approval = False
            perfil.approval_date = timezone.now()
            perfil.save()
            
            # Adicionar ao grupo Cliente
            perfil.user.groups.add(cliente_group)
            count += 1
            
            # Log da ação
            admin_log_message = f'Usuário {perfil.user.username} aprovado por {request.user.username}'
            self.log_change(request, perfil, admin_log_message)
        
        if count:
            self.message_user(request, f'{count} usuário(s) aprovado(s) com sucesso!', messages.SUCCESS)
        else:
            self.message_user(request, 'Nenhum usuário pendente selecionado.', messages.WARNING)
    
    approve_users.short_description = 'Aprovar usuários selecionados'

@admin.register(TwoFactorCode)
class TwoFactorCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
