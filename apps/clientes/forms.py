from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, ClienteEmpresa, Endereco

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'email', 'telefone', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'telefone': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'endereco': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
        }

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ['tipo', 'nome', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casa, Trabalho'}),
            'logradouro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rua, Avenida, etc.'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apto, Bloco, etc.'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000', 'maxlength': 9}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ESTADOS = [
            ('', 'Selecione'),
            ('AC', 'AC'), ('AL', 'AL'), ('AP', 'AP'), ('AM', 'AM'), ('BA', 'BA'),
            ('CE', 'CE'), ('DF', 'DF'), ('ES', 'ES'), ('GO', 'GO'), ('MA', 'MA'),
            ('MT', 'MT'), ('MS', 'MS'), ('MG', 'MG'), ('PA', 'PA'), ('PB', 'PB'),
            ('PR', 'PR'), ('PE', 'PE'), ('PI', 'PI'), ('RJ', 'RJ'), ('RN', 'RN'),
            ('RS', 'RS'), ('RO', 'RO'), ('RR', 'RR'), ('SC', 'SC'), ('SP', 'SP'),
            ('SE', 'SE'), ('TO', 'TO')
        ]
        self.fields['estado'].widget.choices = ESTADOS
        
        # Se for um formulário novo e não tiver o campo tipo definido, definir como "outro"
        if not self.instance.pk and not self.initial.get('tipo'):
            self.initial['tipo'] = 'outro'

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            cep_clean = cep.replace('-', '')
            if not cep_clean.isdigit():
                raise forms.ValidationError('O CEP deve conter apenas números.')
            if len(cep_clean) != 8:
                raise forms.ValidationError('O CEP deve ter 8 dígitos.')
        return cep

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        cliente = self.instance.cliente if self.instance.pk else None
        
        # Verificando se é um endereço principal (obrigatório ter todos os campos)
        if tipo == 'principal':
            campos_obrigatorios = ['logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep']
            for campo in campos_obrigatorios:
                if not cleaned_data.get(campo):
                    self.add_error(campo, f'Este campo é obrigatório para o endereço principal.')
        
        # Verificando duplicidade de tipos
        if tipo and cliente:
            # Verificar se já existe um endereço com o mesmo tipo
            existing = Endereco.objects.filter(cliente=cliente, tipo=tipo, ativo=True).exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(f"Já existe um endereço do tipo '{tipo}' para este cliente.")

        return cleaned_data

class ClienteEmpresaForm(forms.ModelForm):
    class Meta:
        model = ClienteEmpresa
        fields = ['nome', 'email', 'telefone', 'telefone_secundario', 'empresa', 
                 'endereco_principal', 'endereco_cidade', 'endereco_estado', 'endereco_cep', 
                 'endereco_secundario', 'endereco_adicional', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone principal'}),
            'telefone_secundario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone secundário (opcional)'}),
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da empresa (opcional)'}),
            'endereco_principal': forms.HiddenInput(),
            'endereco_cidade': forms.HiddenInput(),
            'endereco_estado': forms.HiddenInput(),
            'endereco_cep': forms.HiddenInput(),
            'endereco_secundario': forms.HiddenInput(),
            'endereco_adicional': forms.HiddenInput(),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observações (opcional)', 'rows': 3}),
        }

# Configurar o Formset para Endereco
EnderecoFormSet = inlineformset_factory(
    ClienteEmpresa,
    Endereco,
    form=EnderecoForm,
    fields=['tipo', 'nome', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep'],
    extra=1,
    max_num=3,
    min_num=1,
    can_delete=True
)