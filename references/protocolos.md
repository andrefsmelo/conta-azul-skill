# API de Protocolos — v1

API da Conta Azul (`protocol-apis-openapi`), **mesmo host e mesma autenticação**:
`https://api-v2.contaazul.com`, header `Authorization: Bearer <token>`. O
`scripts/ca_client.py` chama este endpoint sem alteração.

Serve para **acompanhar operações assíncronas**. Vários `POST` da Conta Azul
(ex.: criar evento financeiro de contas a pagar/receber) **não concluem na
hora**: retornam um `protocolo` com `status: PENDING`. Este endpoint informa o
desfecho real (sucesso, erro e o id do recurso criado).

---

## Endpoint

### `GET /v1/protocolo/{id}` — consultar protocolo
Path: `id` **(obrig.)** — o `protocolo` devolvido pelo POST assíncrono.

**Resposta (`ProtocolResponseDTO`):**
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | string | Identificador do protocolo |
| `status` | enum | `PENDING` \| `SUCCESS` \| `ERROR` |
| `resposta` | string | Mensagem (em `ERROR`, traz o motivo) |
| `evento_financeiro_id` | string | ID do recurso criado (quando `SUCCESS`) |

### Exemplos

`SUCCESS`:
```json
{
  "id": "71145dda-6b52-11f1-907f-4b629fea326b",
  "status": "SUCCESS",
  "resposta": "O evento financeiro foi criado no contas a pagar da Conta Azul.",
  "evento_financeiro_id": "1be7796e-aa64-47a7-bc91-b1a668e699fd"
}
```

`ERROR`:
```json
{
  "id": "732aff3a-6b51-11f1-b10b-932e27c7d307",
  "status": "ERROR",
  "resposta": "A conta financeira de id 00000000-... não existe.",
  "evento_financeiro_id": null
}
```

---

## Padrão de uso (criação assíncrona)

1. `POST` do recurso → recebe `{ "protocolo": "...", "status": "PENDING" }`.
2. Consultar `GET /v1/protocolo/{protocolo}` até sair de `PENDING`.
3. `SUCCESS` → usar `evento_financeiro_id`; `ERROR` → ler `resposta` e corrigir.

> Um `200`/`PENDING` no POST significa apenas **enfileirado** — só o protocolo
> confirma se o recurso foi realmente criado. Ver também a seção "Criação de
> eventos é assíncrona" no [SKILL.md](../SKILL.md).

> Fonte: <https://developers.contaazul.com/docs/protocol-apis-openapi/v1>
