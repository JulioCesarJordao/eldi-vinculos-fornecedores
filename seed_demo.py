"""Inicialização opcional de demonstração, exclusivamente com dados fictícios."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from eldi.models import Loja, Importacao
from eldi.services import importar

password = os.getenv('ELDI_DEMO_PASSWORD')
if password:
    User = get_user_model()
    user = User.objects.filter(username='avaliador').first()
    if user is None:
        candidate = User(username='avaliador')
        validate_password(password, candidate)
        user = User.objects.create_user('avaliador', password=password)
        user.groups.add(Group.objects.get(name='Gestores de TI'))
    shop, _ = Loja.objects.get_or_create(codigo='DEMO', defaults={'nome':'Unidade fictícia'})
    if not Importacao.objects.filter(loja=shop, situacao='concluida').exists():
        raw = b'produto_codigo,produto_descricao,fornecedor_codigo,fornecedor_nome\nP001,Arroz Exemplo 5 kg,,\nP002,Feijao Exemplo 1 kg,,\nP003,Cafe Exemplo 500 g,,\n'
        importar(raw, shop, timezone.now(), user, 'demonstracao.csv')
    print('Demonstração configurada com dados fictícios.')
else:
    print('Defina ELDI_DEMO_PASSWORD no painel para criar a conta de avaliação.')
