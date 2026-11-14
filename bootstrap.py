"""Cria grupos e loja fictícia. Criação de usuários é explícita e interativa."""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config')
import django
django.setup()
from django.contrib.auth.models import Group,Permission
from eldi.models import Loja

for name,codes in [('Compradores',['view_pendencia','change_pendencia']),('Gestores de TI',['view_pendencia','change_pendencia','add_importacao'])]:
    group,_=Group.objects.get_or_create(name=name)
    group.permissions.set(Permission.objects.filter(content_type__app_label='eldi',codename__in=codes))
Loja.objects.get_or_create(codigo='01',defaults={'nome':'Unidade Demonstração'})
print('Grupos e loja fictícia configurados. Crie usuários com createsuperuser ou pelo shell e atribua um grupo. Não há senha padrão.')
