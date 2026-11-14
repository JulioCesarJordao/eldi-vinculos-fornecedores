from django import forms
from django.contrib.auth import get_user_model
from .models import Loja, Pendencia

class ImportForm(forms.Form):
    loja = forms.ModelChoiceField(queryset=Loja.objects.filter(ativa=True))
    referencia = forms.DateTimeField(label='Referência dos dados', widget=forms.DateTimeInput(attrs={'type':'datetime-local'}))
    arquivo = forms.FileField(label='CSV UTF-8 (até 10 MB)')
    def clean_arquivo(self):
        f=self.cleaned_data['arquivo']
        if not f.name.lower().endswith('.csv') or f.size>10*1024*1024:
            raise forms.ValidationError('Selecione CSV de até 10 MB.')
        return f

class AcompanhamentoForm(forms.Form):
    responsavel = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_active=True),required=False,label='Responsável')
    situacao = forms.ChoiceField(label='Situação',choices=[c for c in Pendencia.Situacao.choices if c[0]!='confirmada'])
    observacao = forms.CharField(label='Observação',required=False,max_length=500,widget=forms.Textarea(attrs={'rows':3}))
