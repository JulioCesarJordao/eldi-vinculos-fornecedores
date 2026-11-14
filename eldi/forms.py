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


class AtualizacaoMassaForm(AcompanhamentoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pendencias'].label_from_instance = lambda p: f'{p.produto.codigo} — {p.produto.descricao} | {p.loja.codigo} | {p.get_situacao_display()}'
    pendencias = forms.ModelMultipleChoiceField(
        label='Pendências selecionadas',
        queryset=Pendencia.objects.exclude(situacao='confirmada').select_related('produto','loja').order_by('produto__codigo'),
        widget=forms.CheckboxSelectMultiple,
        help_text='Selecione até 50 registros. Todos receberão os valores abaixo.')
    def clean_pendencias(self):
        selected = self.cleaned_data['pendencias']
        if selected.count() > 50:
            raise forms.ValidationError('Selecione no máximo 50 pendências.')
        return selected
