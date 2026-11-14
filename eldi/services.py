"""Validação de dados e casos de uso transacionais."""
import csv
import hashlib
import io
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Loja, Produto, Fornecedor, Importacao, ItemImportacao, VinculoImportado, Pendencia, HistoricoPendencia

FIELDS = ['produto_codigo','produto_descricao','fornecedor_codigo','fornecedor_nome']

def pode_importar(user):
    return user.is_authenticated and user.is_active and (user.is_superuser or user.has_perm('eldi.add_importacao'))

def parse_csv(raw):
    if len(raw) > 10 * 1024 * 1024:
        raise ValidationError('Arquivo excede 10 MB.')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise ValidationError('Use CSV em UTF-8.')
    reader = csv.DictReader(io.StringIO(text, newline=''), strict=True)
    try:
        if reader.fieldnames != FIELDS:
            raise ValidationError('Cabeçalho inválido. Use: ' + ','.join(FIELDS))
        result, seen, names = {}, set(), {}
        for number, row in enumerate(reader, 2):
            if number > 50001:
                raise ValidationError('Limite de 50 mil linhas excedido.')
            if None in row or any(v is None for v in row.values()):
                raise ValidationError(f'Linha {number}: quantidade de campos inválida.')
            code, desc, supplier, name = [row[k].strip() for k in FIELDS]
            if not code or not desc or len(code)>30 or len(desc)>200:
                raise ValidationError(f'Linha {number}: código ou descrição inválidos.')
            if bool(supplier) != bool(name) or len(supplier)>30 or len(name)>200:
                raise ValidationError(f'Linha {number}: fornecedor incompleto ou inválido.')
            if any('<' in v or '>' in v or '\x00' in v for v in (code,desc,supplier,name)):
                raise ValidationError(f'Linha {number}: conteúdo não permitido.')
            if (code,supplier) in seen:
                raise ValidationError(f'Linha {number}: vínculo duplicado.')
            seen.add((code,supplier))
            item = result.setdefault(code, {'descricao':desc,'fornecedores':{},'sem_fornecedor':False})
            if item['descricao'] != desc:
                raise ValidationError(f'Linha {number}: descrições divergentes para o produto.')
            if (supplier and item['sem_fornecedor']) or (not supplier and item['fornecedores']):
                raise ValidationError(f'Linha {number}: produto declarado com e sem fornecedor no mesmo arquivo.')
            if not supplier:
                item['sem_fornecedor'] = True
            if supplier:
                if supplier in names and names[supplier]!=name:
                    raise ValidationError(f'Linha {number}: nomes divergentes para fornecedor.')
                names[supplier]=name
                item['fornecedores'][supplier]=name
        if not result:
            raise ValidationError('Arquivo sem produtos.')
        return result
    except csv.Error:
        raise ValidationError('CSV malformado.')

def importar(raw, loja, referencia, usuario, filename='arquivo.csv'):
    if not pode_importar(usuario):
        raise PermissionDenied
    if not timezone.is_aware(referencia):
        raise ValidationError('Referência deve informar fuso horário.')
    if referencia > timezone.now():
        raise ValidationError('Referência não pode estar no futuro.')
    digest = hashlib.sha256(raw).hexdigest()
    try:
        data = parse_csv(raw)
        return _aplicar(data,loja,referencia,usuario,filename,digest)
    except ValidationError as exc:
        Importacao.objects.create(loja=loja, usuario=usuario, referencia=referencia, arquivo=filename[:200], digest=digest, situacao='rejeitada', erro='; '.join(exc.messages)[:500])
        raise

@transaction.atomic
def _aplicar(data,loja,referencia,usuario,filename,digest):
    # Serializa importações e atualizações por loja no PostgreSQL.
    locked = Loja.objects.select_for_update().get(pk=loja.pk)
    if not locked.ativa:
        raise ValidationError('Loja inativa.')
    previous = Importacao.objects.filter(loja=loja,situacao='concluida').order_by('-referencia').first()
    if previous and referencia <= previous.referencia:
        raise ValidationError('Use referência posterior à última importação concluída.')
    if Importacao.objects.filter(loja=loja,digest=digest,situacao='concluida').exists():
        raise ValidationError('Este conteúdo já foi importado para a loja.')
    imp = Importacao.objects.create(loja=loja,usuario=usuario,referencia=referencia,arquivo=filename[:200],digest=digest)
    for code, record in data.items():
        product,_ = Produto.objects.update_or_create(codigo=code,defaults={'descricao':record['descricao']})
        item = ItemImportacao.objects.create(importacao=imp,produto=product)
        for supplier,name in record['fornecedores'].items():
            sup,_ = Fornecedor.objects.update_or_create(codigo=supplier,defaults={'nome':name})
            VinculoImportado.objects.create(item=item,fornecedor=sup)
        pending = Pendencia.objects.filter(loja=loja,produto=product).first()
        if record['fornecedores'] and pending is None:
            continue
        old = pending.situacao if pending else ''
        if pending is None:
            pending = Pendencia(loja=loja,produto=product,ultima_importacao=imp)
        if record['fornecedores']:
            pending.situacao = Pendencia.Situacao.CONFIRMADA
            # Uma nova conferência mantém a data da confirmação original.
            if old != Pendencia.Situacao.CONFIRMADA:
                pending.confirmada_em = timezone.now()
        elif pending.situacao == Pendencia.Situacao.CONFIRMADA:
            pending.situacao = Pendencia.Situacao.PENDENTE
            pending.confirmada_em = None
        pending.ultima_importacao = imp
        pending.save()
        HistoricoPendencia.objects.create(pendencia=pending,importacao=imp,usuario=usuario,anterior=old,nova=pending.situacao,descricao='Vínculo conferido no arquivo importado.')
    return imp

@transaction.atomic
def acompanhar(pk,usuario,situacao,responsavel,observacao):
    if not usuario.is_authenticated or not usuario.is_active or not (usuario.is_superuser or usuario.has_perm('eldi.change_pendencia')):
        raise PermissionDenied
    shop_id = Pendencia.objects.values_list('loja_id',flat=True).get(pk=pk)
    Loja.objects.select_for_update().get(pk=shop_id)
    pending = Pendencia.objects.select_for_update().get(pk=pk)
    allowed = [Pendencia.Situacao.PENDENTE,Pendencia.Situacao.ANALISE,Pendencia.Situacao.INFORMADA]
    if pending.situacao==Pendencia.Situacao.CONFIRMADA or situacao not in allowed:
        raise ValidationError('Confirmação ou reabertura depende de importação posterior.')
    if responsavel and (not responsavel.is_active or not (responsavel.is_superuser or responsavel.has_perm('eldi.change_pendencia'))):
        raise ValidationError('Responsável não autorizado ou inativo.')
    if len(observacao)>500 or '<' in observacao or '>' in observacao:
        raise ValidationError('Use até 500 caracteres de texto simples.')
    old = pending.situacao
    detail = f'Responsável anterior: {pending.responsavel_id}; novo: {responsavel.pk if responsavel else None}. Observação: {observacao}'
    pending.situacao, pending.responsavel, pending.observacao = situacao,responsavel,observacao
    pending.save()
    HistoricoPendencia.objects.create(pendencia=pending,usuario=usuario,anterior=old,nova=situacao,descricao=detail[:700])
    return pending
