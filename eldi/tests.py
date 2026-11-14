from datetime import timedelta
from django.test import TestCase, SimpleTestCase, Client
from django.core.exceptions import ValidationError,PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Loja,Produto,Importacao,Pendencia,HistoricoPendencia,VinculoImportado
from .services import parse_csv,importar,acompanhar

HEADER=b'produto_codigo,produto_descricao,fornecedor_codigo,fornecedor_nome\n'

class CsvUnitTests(SimpleTestCase):
    def test_utf8_bom_and_leading_zero(self):
        self.assertIn('001',parse_csv(b'\xef\xbb\xbf'+HEADER+b'001,Arroz,,\n'))
    def test_multiple_suppliers(self):
        data=parse_csv(HEADER+b'P1,Arroz,F1,Fornecedor A\nP1,Arroz,F2,Fornecedor B\n')
        self.assertEqual(len(data['P1']['fornecedores']),2)
    def test_invalid_inputs(self):
        invalid=[b'wrong\n',HEADER,HEADER+b',Arroz,,\n',HEADER+b'P1,Arroz,F1,\n',HEADER+b'P1,Arroz,,extra,extra\n',HEADER+b'P1,<script>,,\n',HEADER+b'P1,Arroz,,\nP1,Arroz,,\n',HEADER+b'P1,Arroz,F1,A\nP2,Cafe,F1,B\n',b'\xff']
        for raw in invalid:
            with self.subTest(raw=raw),self.assertRaises(ValidationError): parse_csv(raw)

class WorkflowTests(TestCase):
    def setUp(self):
        User=get_user_model()
        self.manager=User.objects.create_superuser('gestor',password='Teste-local-com-frase-segura')
        self.buyer=User.objects.create_user('comprador',password='Teste-local-com-frase-segura')
        self.buyer.user_permissions.add(*Permission.objects.filter(codename__in=['view_pendencia','change_pendencia']))
        self.shop=Loja.objects.create(codigo='01',nome='Demonstração')
        self.other=Loja.objects.create(codigo='02',nome='Outra')
        self.ref=timezone.now()-timedelta(days=3)
    def run_import(self,rows,step=0,shop=None):
        return importar(HEADER+rows.encode(),shop or self.shop,self.ref+timedelta(hours=step),self.manager)
    def test_pending_and_supplier(self):
        self.run_import('P1,Arroz,,\nP2,Cafe,F1,Fornecedor\n')
        self.assertEqual(list(Pendencia.objects.values_list('produto__codigo',flat=True)),['P1'])
        self.assertEqual(VinculoImportado.objects.count(),1)
    def test_absent_preserves_status_and_last_verification(self):
        first=self.run_import('P1,Arroz,,\nP2,Cafe,,\n')
        p=Pendencia.objects.get(produto__codigo='P2')
        acompanhar(p.pk,self.buyer,'informada',self.buyer,'Corrigido no Consinco')
        self.run_import('P1,Arroz,F1,Fornecedor\n',1)
        p.refresh_from_db()
        self.assertEqual(p.situacao,'informada')
        self.assertEqual(p.ultima_importacao_id,first.pk)
        self.assertEqual(Pendencia.objects.get(produto__codigo='P1').situacao,'confirmada')
    def test_reopen_keeps_owner(self):
        self.run_import('P1,Arroz,,\n')
        p=Pendencia.objects.get()
        acompanhar(p.pk,self.buyer,'analise',self.buyer,'Conferir')
        self.run_import('P1,Arroz,F1,Fornecedor\n',1)
        self.run_import('P1,Arroz revisado,,\n',2)
        p.refresh_from_db()
        self.assertEqual(p.situacao,'pendente')
        self.assertEqual(p.responsavel,self.buyer)
        self.assertIsNone(p.confirmada_em)
    def test_invalid_import_does_not_partially_update(self):
        with self.assertRaises(ValidationError): self.run_import('P1,Arroz,,\nP2,Cafe,F1,\n')
        self.assertFalse(Produto.objects.exists())
        self.assertFalse(Pendencia.objects.exists())
        self.assertEqual(Importacao.objects.get().situacao,'rejeitada')
    def test_old_and_duplicate_rejected(self):
        self.run_import('P1,Arroz,,\n')
        with self.assertRaises(ValidationError): self.run_import('P2,Cafe,,\n',-1)
        with self.assertRaises(ValidationError): self.run_import('P1,Arroz,,\n',1)
        self.assertEqual(Importacao.objects.filter(situacao='concluida').count(),1)
    def test_shop_isolation(self):
        self.run_import('P1,Arroz,,\n')
        self.run_import('P1,Arroz,F1,Fornecedor\n',1,self.other)
        self.assertEqual(Pendencia.objects.get(loja=self.shop).situacao,'pendente')
    def test_cannot_confirm_manually(self):
        self.run_import('P1,Arroz,,\n')
        with self.assertRaises(ValidationError): acompanhar(Pendencia.objects.get().pk,self.buyer,'confirmada',self.buyer,'')
    def test_confirmed_is_locked(self):
        self.run_import('P1,Arroz,,\n')
        self.run_import('P1,Arroz,F1,Fornecedor\n',1)
        with self.assertRaises(ValidationError): acompanhar(Pendencia.objects.get().pk,self.buyer,'analise',None,'')
    def test_buyer_cannot_import(self):
        with self.assertRaises(PermissionDenied): importar(HEADER+b'P1,Arroz,,\n',self.shop,self.ref,self.buyer)
    def test_owner_and_note_validation(self):
        self.run_import('P1,Arroz,,\n')
        self.buyer.is_active=False; self.buyer.save()
        p=Pendencia.objects.get()
        with self.assertRaises(ValidationError): acompanhar(p.pk,self.manager,'analise',self.buyer,'')
        with self.assertRaises(ValidationError): acompanhar(p.pk,self.manager,'analise',None,'<script>')
    def test_history_preserved(self):
        self.run_import('P1,Arroz,,\n')
        acompanhar(Pendencia.objects.get().pk,self.buyer,'informada',self.buyer,'Conferido')
        self.assertEqual(HistoricoPendencia.objects.count(),2)
    def test_http_permissions_csrf_and_rendering(self):
        self.assertEqual(self.client.get('/').status_code,302)
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get('/importar/').status_code,403)
        self.assertEqual(self.client.get('/pendencias/').status_code,200)
        csrf=Client(enforce_csrf_checks=True);csrf.force_login(self.manager)
        self.assertEqual(csrf.post('/importar/',{}).status_code,403)
    def test_http_import_and_search(self):
        self.client.force_login(self.manager)
        response=self.client.post('/importar/',{'loja':self.shop.pk,'referencia':self.ref.isoformat(),'arquivo':SimpleUploadedFile('demo.csv',HEADER+b'P1,Arroz,,\n')})
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Conferência concluída')
        self.assertContains(self.client.get('/pendencias/',{'q':'P1'}),'Arroz')
        p=Pendencia.objects.get()
        self.assertEqual(self.client.get(f'/pendencias/{p.pk}/').status_code,200)
        res=self.client.post(f'/pendencias/{p.pk}/',{'situacao':'analise','responsavel':self.buyer.pk,'observacao':'Revisar'})
        self.assertEqual(res.status_code,302)
    def test_future_reference_rejected(self):
        with self.assertRaises(ValidationError): importar(HEADER+b'P1,Arroz,,\n',self.shop,timezone.now()+timedelta(days=1),self.manager)
