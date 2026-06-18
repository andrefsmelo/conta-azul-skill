# Erros comuns na integração

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
