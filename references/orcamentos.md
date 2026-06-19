# API de Orçamentos — v1

API da Conta Azul (`open-api-proposal`), **mesmo host e mesma autenticação**:
`https://api-v2.contaazul.com`, header `Authorization: Bearer <token>`. O
`scripts/ca_client.py` chama estes endpoints sem alteração.

Gerencia **orçamentos** (propostas). Estrutura próxima à de Vendas — um orçamento
aceito vira venda.

Convenções: paginação por `pagina`/`tamanho_pagina`; datas `YYYY-MM-DD`.
**(obrig.)** = obrigatório.

---

## Endpoints

### `GET /v1/orcamentos` — listar/filtrar
Sem obrigatórios. Filtros (query): `pagina`, `tamanho_pagina`, `termo_busca`,
`data_inicio`/`data_fim`, `data_criacao_de`/`_ate`, `data_alteracao_de`/`_ate`,
`ids_vendedores`, `ids_clientes`, `ids_produtos`, `ids_categorias`,
`ids_natureza_operacao`, `situacoes`, `origens`, `numeros`. Ordenação por
`DATA` \| `NUMERO` \| `CLIENTE`.

### `POST /v1/orcamentos` — criar
Body: `CriarOrcamento` (abaixo).

### `GET /v1/orcamentos/{id}` — detalhar
Path: `id` **(obrig.)**.

### `DELETE /v1/orcamentos` — excluir em lote
**Leva corpo** (`ExclusaoLoteOrcamento`): `{ "ids": ["<uuid>", ...] }`. Use
`delete --body`.

---

## Schema: CriarOrcamento

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_cliente`* | string | Cliente |
| `data_orcamento`* | string | `YYYY-MM-DD` |
| `data_validade`* | string | `YYYY-MM-DD` |
| `itens`* | array<CriarItemOrcamento> | ≥1 item |
| `id_vendedor` | string | Vendedor |
| `descricao` | string | |
| `composicao_de_valor` | objeto | `frete` + `desconto` |
| `previsao_entrega` | string | |
| `observacoes` / `observacoes_pagamento` | string | |

### CriarItemOrcamento
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id`* | string | ID do produto ou serviço |
| `quantidade` | number | > 0 |
| `valor` | number | Valor unitário (> 0) |
| `valor_custo` | number | |

### Exemplo mínimo
```json
{
  "id_cliente": "<uuid>",
  "data_orcamento": "2026-06-19",
  "data_validade": "2026-07-19",
  "itens": [{ "id": "<uuid_produto>", "quantidade": 1, "valor": 100.0 }]
}
```

---

## Enums

- **TipoDeSituacaoOrcamento**: `ORCAMENTO`, `ORCAMENTO_ACEITO`,
  `ORCAMENTO_RECUSADO`.
- **TipoItemOrcamento**: `PRODUTO`, `SERVICO`.
- **TipoDeItens**: `PRODUTO`, `SERVICO`, `PRODUTO_E_SERVICO`.
- **TipoDeDesconto**: `PORCENTAGEM`, `VALOR`.

> Fonte: <https://developers.contaazul.com/docs/open-api-proposal/v1>
