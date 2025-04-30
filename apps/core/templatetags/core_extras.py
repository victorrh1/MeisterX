from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite acessar itens de um dicionário através de uma chave dinâmica nos templates
    Exemplo: {{ meu_dicionario|get_item:chave_dinamica }}
    """
    return dictionary.get(key, None) 