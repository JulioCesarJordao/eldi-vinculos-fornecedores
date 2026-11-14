# Escopo inicial

## Requisitos obrigatórios planejados

- RF01: importar e validar CSV por loja e referência temporal, sem alterações parciais.
- RF02: identificar ausência de vínculo e manter uma pendência por produto e loja.
- RF03: consultar por código/descrição, loja e situação.
- RF04: atribuir responsável ativo.
- RF05: registrar observações e situação com histórico.
- RF06: confirmar regularização somente com vínculo válido em dados posteriores do mesmo contexto.

RF07, painel gerencial, é desejável e não bloqueia a entrega inicial.

## Regras críticas

Regularização informada é distinta de confirmada. Produto ausente em novo arquivo mantém a situação anterior e é indicado como não verificado. Um produto pode ter vários fornecedores. Importações antigas não substituem verificações posteriores.

## Modelo planejado

Usuario, Loja, Produto, Fornecedor, Importacao, ItemImportacao, VinculoImportado, Pendencia e HistoricoPendencia. A separação entre item presente e vínculo observado permite distinguir ausência de fornecedor de ausência do produto no arquivo.

## Fora de escopo

Integração direta/alterações automáticas no Consinco, gestão comercial completa, aplicativo móvel nativo e operação offline.

## Validação

Executar três tarefas: localizar pendência, atualizar acompanhamento por teclado e interpretar a conferência. Metas iniciais: três tarefas sem ajuda; acompanhamento em até 180 segundos; satisfação mínima 4/5. Confirmar participante e consentimento antes de cada sessão. Duas rodadas reais e ajustes serão documentados quando realizados.
