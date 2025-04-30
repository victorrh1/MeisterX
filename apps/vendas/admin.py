from django.contrib import admin
from .models import MetodoEnvio, FormaPagamento, Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 1
    readonly_fields = ['valor_total']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_cliente_nome', 'data_venda', 'status', 'valor_total']
    list_filter = ['status', 'data_venda', 'forma_pagamento', 'metodo_envio']
    search_fields = ['cliente_nome', 'cliente_email', 'cliente_cadastrado__nome']
    readonly_fields = ['subtotal', 'valor_total']
    inlines = [ItemVendaInline]
    fieldsets = (
        ('Informações da Venda', {
            'fields': ('usuario_vendedor', 'status', 'data_venda', 'data_modificacao')
        }),
        ('Cliente', {
            'fields': ('cliente_cadastrado', 'cliente_nome', 'cliente_email', 'cliente_telefone')
        }),
        ('Pagamento e Entrega', {
            'fields': ('forma_pagamento', 'metodo_envio', 'codigo_rastreamento')
        }),
        ('Endereço de Entrega', {
            'fields': ('endereco_entrega', 'cidade_entrega', 'estado_entrega', 'cep_entrega')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto_percentual', 'desconto_valor', 'valor_frete', 'valor_total')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    def get_cliente_nome(self, obj):
        return obj.cliente_cadastrado.nome if obj.cliente_cadastrado else obj.cliente_nome
    get_cliente_nome.short_description = 'Cliente'
    
    def get_readonly_fields(self, request, obj=None):
        # Se o objeto já está criado, torna alguns campos somente leitura
        if obj:
            return self.readonly_fields + ['data_venda', 'data_modificacao']
        return self.readonly_fields

@admin.register(MetodoEnvio)
class MetodoEnvioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'taxa_fixa', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome'] 