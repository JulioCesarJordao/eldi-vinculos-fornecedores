# Executar a implementação Django

O protótipo estático da raiz permanece separado. Abrir `index.html` executa apenas a simulação antiga, não o backend.

## Desenvolvimento local — PowerShell

Python 3.12 ou 3.13 compatível. Validação local realizada com Python 3.12.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
$env:ELDI_DEBUG='1'
.venv/Scripts/python manage.py migrate
.venv/Scripts/python bootstrap.py
.venv/Scripts/python manage.py createsuperuser
.venv/Scripts/python manage.py runserver 127.0.0.1:8000
```

Acesse `http://127.0.0.1:8000/`. Não existe senha padrão: `createsuperuser` solicita uma senha local. Não exponha runserver nem DEBUG à rede pública. A base local SQLite é uma alternativa explícita para desenvolvimento, não a implantação corporativa planejada.

Para criar comprador, execute `manage.py shell`, utilize `get_user_model().objects.create_user` com senha definida de forma segura e atribua ao grupo `Compradores` criado por bootstrap. Não publique credenciais. O superusuário inicial administra a instalação; permissões comuns devem ser atribuídas por grupo.

## PostgreSQL

Configure antes de migrar: `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT` e `ELDI_SECRET_KEY`. Desative `ELDI_DEBUG`, configure `ELDI_HOSTS` e execute `manage.py migrate`. O banco deve ser criado pelo administrador; não exponha sua porta publicamente. A implantação requer servidor WSGI, HTTPS, arquivos estáticos e backups. Não é realizada por este roteiro local.

## Formato CSV

Cabeçalho obrigatório, delimitador vírgula e codificação UTF-8:

```csv
produto_codigo,produto_descricao,fornecedor_codigo,fornecedor_nome
P001,Arroz Exemplo 5 kg,,
P002,Cafe Exemplo 500 g,F010,Fornecedor Exemplo
```

Use referência com fuso interpretado no horário de São Paulo; a referência não pode ser futura nem anterior/igual à última importação concluída da loja. Um produto sem vínculo precisa constar com campos de fornecedor vazios. Vários fornecedores são representados em linhas distintas. O CSV representa os dados disponíveis; não recupera vínculos ausentes da exportação.

## Testes

```powershell
$env:ELDI_TESTING='1'
.venv/Scripts/python manage.py check
.venv/Scripts/python manage.py makemigrations --check --dry-run
.venv/Scripts/python -m coverage run manage.py test eldi
.venv/Scripts/python -m coverage report -m
```

Com PostgreSQL configurado, os testes usam banco de teste separado; a conta de teste precisa de permissão para criá-lo. Nunca executar contra base de produção. O ambiente deve ser dedicado à homologação.

## Limitações conhecidas

- 24 testes aprovados em SQLite; migrações aplicadas em base local descartável. O pipeline usa PostgreSQL 16; consulte a execução do commit atual. Testes de concorrência real continuam pendentes.
- Cobertura de linhas local: 96%, excluindo testes e migrações; não equivale a cobertura de cenários ou prova de segurança.
- Sem limitação de tentativas de login e fluxo de convite/reset de senha nesta primeira entrega. RNF01 ainda não está integralmente atendido.
- CI configurada no GitHub Actions, com build, testes PostgreSQL e cobertura mínima de 90%; PR #1 registra a revisão técnica.
- Sem medição de desempenho do RNF03 nem auditoria completa de acessibilidade.
- Duas rodadas com compradora realizadas em 14/11/2026, conforme relato do estudante, motivaram a atualização em massa. A edição em tabela ficou como sugestão futura.
- Importações são síncronas e serializadas por loja no PostgreSQL; testes de concorrência e volume ainda necessários. SQLite não fornece a mesma garantia de bloqueio.
- Telas Django funcionais usam apresentação simplificada, diferente do protótipo visual. Resultado da importação encaminha para a lista, sem painel gerencial.
