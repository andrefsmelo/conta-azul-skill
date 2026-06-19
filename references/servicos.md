# API de Serviços — v1

API da Conta Azul (`open-api-service`), **mesmo host e mesma autenticação**:
`https://api-v2.contaazul.com`, header `Authorization: Bearer <token>`. O
`scripts/ca_client.py` chama estes endpoints sem alteração.

Gerencia o **catálogo de serviços** (prestados/tomados) — usados em vendas,
contratos e notas fiscais de serviço.

Convenções: paginação por `pagina`/`tamanho_pagina`. **(obrig.)** = obrigatório.

---

## Endpoints

### `GET /v1/servicos` — listar/filtrar
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` / `tamanho_pagina` | integer | paginação |
| `busca_textual` | string | busca por texto |

### `POST /v1/servicos` — criar
Body: `CriarServico`:
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `descricao`* | string | Descrição do serviço |
| `codigo` | string | Código interno |
| `preco` | number | Preço de venda |
| `custo` | number | Custo |
| `status` | enum | `ATIVO` \| `INATIVO` |
| `tipo_servico` | enum | `PRESTADO` \| `TOMADO` \| `AMBOS` |

### `GET /v1/servicos/{id}` — detalhar
Path: `id` **(obrig.)**.

### `PATCH /v1/servicos/{id}` — atualizar (parcial)
Path: `id` **(obrig.)**. Body: `AtualizacaoParcialServico` (campos a alterar).

### `DELETE /v1/servicos` — excluir em lote
**Leva corpo** (incomum para DELETE): `{ "ids": [<int>, ...] }`. O cliente
suporta `delete --body`.

---

## Enums

- **StatusDoServico**: `ATIVO`, `INATIVO`.
- **TipoDeServico**: `PRESTADO`, `TOMADO`, `AMBOS`.

### Exemplo (criar)
```json
{ "descricao": "Consultoria", "preco": 250.00, "tipo_servico": "PRESTADO" }
```

> Atenção: o `DELETE` em lote usa **ids inteiros** (`id_legado`), não os UUIDs.

> Fonte: <https://developers.contaazul.com/open-api-docs/open-api-service/v1>
