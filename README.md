# Sistema de Acompanhamento de Vínculos entre Produtos e Fornecedores da Rede Eldi

Projeto acadêmico de Análise e Desenvolvimento de Sistemas — Projeto de Software.

## Problema

Após uma migração para o Consinco, permaneceram produtos sem vínculo com fornecedores. A proposta é apoiar compradores na identificação e no acompanhamento dessas pendências. As correções cadastrais continuam no Consinco.

## Estado atual

O repositório contém o protótipo da Experiência Prática II e uma primeira implementação Django: autenticação, permissões, modelos, migração inicial, importação transacional, consulta e acompanhamento com histórico. O histórico começa pela importação do protótipo existente, sem commits retroativos. A execução local foi validada com Python 3.12 e SQLite; PostgreSQL está configurável, mas ainda não foi testado neste ambiente. Não é uma versão pronta para produção.

## Executar o protótipo

Abra `index.html` em um navegador atualizado. Alternativamente, com Python instalado, execute na raiz:

```sh
python -m http.server 8000
```

Acesse `http://localhost:8000/`.

1. Abra **Consultar pendências** e busque `P001`.
2. Selecione **Acompanhar**, atribua responsável e registre a situação.
3. Abra **Importar arquivo**, selecione **Usar arquivo fictício** e **Validar e importar**.
4. Confira `P002` confirmado e `P003` não verificado, preservando sua situação anterior.
5. Use **Restaurar demonstração** para recomeçar.

## Limitações da demonstração

- Dados exclusivamente fictícios; não utilizar arquivos comerciais ou credenciais reais.
- Login e perfis são simulados, sem autenticação segura no servidor.
- Alterações usam armazenamento local do navegador quando disponível.
- A importação aceita apenas o CSV de exemplo e não se conecta ao Consinco.
- As telas não comprovam os requisitos completos de segurança, desempenho e acessibilidade.

## Implementação planejada

Python 3.13, Django 5.2 LTS, PostgreSQL e Psycopg 3; arquitetura monolítica em camadas; telas HTML/CSS. Versões e dependências deverão ser verificadas e fixadas durante a implementação.

O fluxo obrigatório inclui importação validada, identificação de pendências, consulta com filtros, atribuição de responsável, registro de acompanhamento e confirmação por importação posterior. Produto ausente do arquivo **não** é considerado regularizado.

## Próximas etapas da Experiência Prática III

- Implementar os requisitos funcionais no backend e banco de dados.
- Adicionar testes unitários e de integração e executar análise de cobertura.
- Configurar integração contínua e registrar seus resultados reais.
- Desenvolver em branches com commits semânticos e revisão/autorrevisão por Pull Request.
- Conduzir duas rodadas de validação com participante real e autorizado, registrando feedback e ajustes.

Esses itens são planejados e não constituem evidência de execução.

## Organização

```text
index.html, app.js, style.css  Interface navegável
vinculos_demo.csv              Dados fictícios de exemplo
ESCOPO.md                     Requisitos e limites
DESENVOLVIMENTO.md             Fluxo de contribuição e evidências
```

## Impacto esperado

Contribuição local ao ODS 8, meta 8.2, pelo apoio à organização e produtividade do trabalho. Benefícios e metas ainda precisam de validação; não se pressupõe ganho de renda ou de abastecimento.

Projeto acadêmico independente; não é um produto oficial da Consinco nem uma divulgação de dados internos da Rede Eldi.




## Atualização após validação — novembro de 2026

A aplicação Django inclui atualização em massa: selecione até 50 pendências, informe responsável, situação e observação, revise e confirme. O histórico é individual e a transação desfaz o lote em caso de falha. Regularizações confirmadas continuam dependendo da importação, sem edição manual.

O fluxo foi implementado após sugestão de uma compradora participante da validação, conforme relato do estudante. A proposta posterior de campos editáveis em cada linha permanece como evolução futura, não implementada nesta versão.

Validação local: 24 testes em SQLite. A integração contínua em `.github/workflows/ci.yml` executa build/verificações, testes com PostgreSQL 16 e cobertura mínima de 90%. Consulte o resultado da execução correspondente ao commit atual; execuções anteriores não validam alterações posteriores.

A demonstração usa dados fictícios. Não há senha padrão no repositório. O desenvolvimento local não representa implantação de produção.
