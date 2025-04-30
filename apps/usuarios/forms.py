from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

def validate_cpf(value):
    if not value:  # Se o valor for vazio, retorna (já que o campo é opcional)
        return
    
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', value)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        raise forms.ValidationError('CPF inválido.')
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        raise forms.ValidationError('CPF inválido.')

    # Validação do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[9]):
        raise forms.ValidationError('CPF inválido.')

    # Validação do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[10]):
        raise forms.ValidationError('CPF inválido.')

class PerfilForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 bg-gray-50 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    nome_completo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    cpf = forms.CharField(
        required=False,
        max_length=14,
        validators=[validate_cpf],
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': '000.000.000-00'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'nome_completo', 'cpf']
        labels = {
            'nome_completo': 'Nome Completo',
            'cpf': 'CPF'
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove caracteres não numéricos
            cpf = re.sub(r'[^0-9]', '', cpf)
            # Formata o CPF
            cpf = f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'
        return cpf

class CustomPasswordChangeForm(PasswordChangeForm):
    error_message_password = "A senha deve conter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }),
        label='Senha atual'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }),
        label='Nova senha'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }),
        label='Confirme a nova senha'
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # Define os padrões de validação
        patterns = {
            r'.{8,}': 'tamanho mínimo de 8 caracteres',
            r'[A-Z]': 'letra maiúscula',
            r'[a-z]': 'letra minúscula',
            r'[0-9]': 'número',
            r'[!@#$%^&*(),.?":{}|<>]': 'caractere especial'
        }
        
        # Verifica todos os padrões
        for pattern in patterns:
            if not re.search(pattern, password):
                raise forms.ValidationError(self.error_message_password)
        
        return password 