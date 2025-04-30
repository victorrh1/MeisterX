from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from apps.vendas.models import ItemVenda


@receiver(post_save, sender=ItemVenda)
def atualizar_estoque_produto(sender, instance, created, **kwargs):
    """
    Quando um novo item é adicionado à venda, reduz o estoque do produto correspondente
    """
    if created:  # Apenas quando o item é criado, não quando é atualizado
        produto = instance.produto
        if produto.estoque >= instance.quantidade:
            produto.estoque -= instance.quantidade
            produto.save(update_fields=['estoque'])


@receiver(pre_delete, sender=ItemVenda)
def restaurar_estoque_produto(sender, instance, **kwargs):
    """
    Quando um item é removido da venda, restaura o estoque do produto
    """
    # Verificar se a venda não está cancelada antes de restaurar o estoque
    if instance.venda.status != 'cancelado':
        produto = instance.produto
        produto.estoque += instance.quantidade
        produto.save(update_fields=['estoque']) 