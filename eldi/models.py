from django.conf import settings
from django.db import models

class Loja(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=150)
    ativa = models.BooleanField(default=True)
    def __str__(self): return f'{self.codigo} — {self.nome}'

class Produto(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    descricao = models.CharField(max_length=200)

class Fornecedor(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=200)

class Importacao(models.Model):
    loja = models.ForeignKey(Loja, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    referencia = models.DateTimeField()
    recebida_em = models.DateTimeField(auto_now_add=True)
    arquivo = models.CharField(max_length=200)
    digest = models.CharField(max_length=64)
    situacao = models.CharField(max_length=20, default='concluida')
    erro = models.CharField(max_length=500, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['loja','referencia'], condition=models.Q(situacao='concluida'), name='referencia_concluida_unica')]

class ItemImportacao(models.Model):
    importacao = models.ForeignKey(Importacao, on_delete=models.PROTECT, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['importacao','produto'], name='item_unico')]

class VinculoImportado(models.Model):
    item = models.ForeignKey(ItemImportacao, on_delete=models.PROTECT, related_name='vinculos')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['item','fornecedor'], name='vinculo_unico')]

class Pendencia(models.Model):
    class Situacao(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ANALISE = 'analise', 'Em análise'
        INFORMADA = 'informada', 'Regularização informada'
        CONFIRMADA = 'confirmada', 'Regularização confirmada'
    loja = models.ForeignKey(Loja, on_delete=models.PROTECT)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.PENDENTE, db_index=True)
    observacao = models.CharField(max_length=500, blank=True)
    ultima_importacao = models.ForeignKey(Importacao, on_delete=models.PROTECT)
    aberta_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)
    confirmada_em = models.DateTimeField(null=True, blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['loja','produto'], name='pendencia_unica'), models.CheckConstraint(condition=models.Q(situacao__in=['pendente','analise','informada','confirmada']), name='situacao_valida')]

class HistoricoPendencia(models.Model):
    pendencia = models.ForeignKey(Pendencia, on_delete=models.PROTECT, related_name='historico')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    importacao = models.ForeignKey(Importacao, on_delete=models.PROTECT, null=True)
    ocorrido_em = models.DateTimeField(auto_now_add=True)
    anterior = models.CharField(max_length=20, blank=True)
    nova = models.CharField(max_length=20)
    descricao = models.CharField(max_length=700)
    class Meta:
        ordering = ['-ocorrido_em','-pk']
