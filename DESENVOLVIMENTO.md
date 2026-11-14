# Desenvolvimento e evidências

## Histórico

O primeiro commit incorpora o protótipo existente. Novas funcionalidades devem ser registradas conforme forem desenvolvidas, sem fabricar datas, revisões ou resultados.

## Organização das mudanças

Usar branches curtas, como `feat/importacao-csv`, e mensagens no formato `tipo(escopo): descrição`.

Exemplos: `feat(importacao): validar cabeçalhos do CSV`, `test(vinculos): cobrir produto ausente`, `docs(execucao): documentar configuração local`.

## Pull Requests

Descrever problema, comportamento final, testes efetivamente executados e limitações. Na autorrevisão, conferir arquivos alterados, regras de negócio, acesso e dados expostos. Não declarar aprovação de outra pessoa quando não houve revisor.

## Proteção de dados

Publicar apenas código, exemplos fictícios e documentação sem informações comerciais sensíveis. Não incluir exportações reais do Consinco, senhas, tokens, configuração interna, backups ou dados de participantes. Segredos devem permanecer fora do repositório.

## Evidências futuras

Registrar links reais dos commits, PRs e execuções de CI. Preservar relatórios de testes e cobertura. Registrar validações com data, versão, tarefas, resultados, feedback autorizado e mudanças implementadas. A documentação de planos não substitui a execução.
