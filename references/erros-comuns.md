# Erros comuns na integração

As seções abaixo (`invalid_grant`, `401`, `429`, `500`) refletem a página oficial
de [erros comuns](https://developers.contaazul.com/commonmistakes). A seção final
("Validação e armadilhas reais") reúne erros observados em chamadas reais às APIs.

## `invalid_grant` (OAuth)
O `authorization_code` ou `refresh_token` é inválido, já foi usado, expirou, ou
não bate com `redirect_uri`/`client_id`.

Causas: código já trocado por tokens; `refresh_token` expirado/revogado;
`redirect_uri` diferente do cadastrado; `client_id` incorreto.

## `401 Unauthorized`
Requisição não autenticada ou credenciais inválidas.

Causas: `access_token` ausente/ inválido no header `Authorization: Bearer`;
token expirado (renove com `refresh_token`); falta de permissão para o recurso.

## `429 Too Many Requests`
Excedeu o rate limit: **600 chamadas/minuto** e **até 10/segundo** por conta ERP
conectada.

O que fazer: backoff exponencial; monitore headers de rate limit; reduza
chamadas com cache.

## `500 Internal Server Error`
Erro genérico do servidor da Conta Azul.

Causas: erro interno da API; infra temporária; corpo JSON malformado ou dados
inconsistentes.

O que fazer: validar formato/dados da requisição; reenviar após alguns segundos;
se persistir, contatar o suporte no Portal do Desenvolvedor.

## `401` com mensagem de conta do ERP
Mensagem: *"...utilize o usuário e senha do ERP e tente novamente"*. O token é
válido, mas foi gerado autorizando com a **conta do Portal do Desenvolvedor** em
vez de uma **conta do ERP**. Refaça o login OAuth usando uma conta do ERP. Ver
[autenticacao.md](autenticacao.md).

## `400` de redirecionamento — `redirect_mismatch`
Na tela de login (`auth.contaazul.com/error?error=redirect_mismatch`): o
`redirect_uri` enviado **não é idêntico** ao cadastrado no app. Use exatamente o
valor do Portal do Desenvolvedor (incluindo `https://`, `www`, barra final).

---

## Validação e armadilhas reais (observadas em chamadas reais)

Estas não estão na página oficial, mas a API as retorna como `HTTP 400` ou impõe
como regra. Documentadas durante testes contra o ambiente real.

| Sintoma / mensagem | Causa | Correção |
| --- | --- | --- |
| `400` "o tamanho da página deve ser um dos seguintes valores..." | `tamanho_pagina` fora do enum permitido | Use `10, 20, 50, 100, 200, 500, 1000` (Notas Fiscais: só `10,20,50,100`) |
| `400` "rateio: Deve possuir pelo menos uma categoria..." | Criação de evento financeiro sem `rateio` | Inclua ≥1 categoria no `rateio` |
| `400` "valor da parcela: O valor líquido deve ser informado." | Falta `valor_liquido` em `detalhe_valor` | Envie `valor_liquido` junto do `valor_bruto` |
| `400` "O período entre ... não pode ser maior que 15 dias" | Janela de datas grande em Notas Fiscais | Pagine por janelas de até 15 dias |
| Protocolo `ERROR` "A conta financeira de id ... não existe." | Referência (`conta_financeira`, `contato`, etc.) inexistente no ERP | Use IDs reais (liste via `GET`); contas financeiras são criadas no ERP, não pela API |
| `POST` retorna `PENDING` e o recurso "não aparece" | Criação é **assíncrona** — o `200` só enfileira | Consulte `GET /v1/protocolo/{id}` até `SUCCESS`/`ERROR` (ver [protocolos.md](protocolos.md)) |
| Parser quebra ao ler o total da resposta | **Envelope varia por API** | Total pode estar em `itens_totais`, `totalItems`, `total_items`, `total_itens` ou `paginacao.total_itens` — confira por endpoint |
| `nano`/CLI: "terminal is not fully functional" | `TERM` desconhecido na máquina remota (ex.: Ghostty) | `export TERM=xterm-256color` antes do comando |
