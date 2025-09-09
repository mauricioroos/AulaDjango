from django import forms
from .models import Cliente, Perfil

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ('nome', 'email')

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ('telefone', 'rua', 'numero', 'cep', 'bairro', 'cidade', 'complemento')