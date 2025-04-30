from django import forms
from .models import Produto, ProdutoEmpresa

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'estoque']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'preco': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'step': '0.01'}),
            'estoque': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
        }

class ProdutoEmpresaForm(forms.ModelForm):
    class Meta:
        model = ProdutoEmpresa
        fields = ['nome', 'descricao', 'preco', 'estoque', 'imagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição', 'rows': 3}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço', 'step': '0.01'}),
            'estoque': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade em estoque'}),
        } 