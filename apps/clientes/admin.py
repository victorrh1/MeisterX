from django.contrib import admin
from .models import Cliente, ClienteEmpresa

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'data_cadastro']
    search_fields = ['nome', 'email', 'telefone']
    list_filter = ['data_cadastro']
    ordering = ['-data_cadastro']

@admin.register(ClienteEmpresa)
class ClienteEmpresaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario_proprietario', 'email', 'telefone', 'empresa', 'data_cadastro', 'ativo']
    search_fields = ['nome', 'email', 'telefone', 'empresa']
    list_filter = ['data_cadastro', 'ativo', 'usuario_proprietario']
    ordering = ['-data_cadastro']
    readonly_fields = ['data_cadastro']
    list_editable = ['ativo']
