# API de Vendas — v1

API da Conta Azul (`sales-apis-openapi`), **mesmo host e mesma autenticação**:
`https://api-v2.contaazul.com`, header `Authorization: Bearer <token>`. O
`scripts/ca_client.py` chama estes endpoints sem alteração.

Gerencia **vendas/orçamentos**: criação, consulta, edição, exclusão, itens,
PDF e vendedores.

Convenções: `tamanho_pagina` aceita `10, 20, 50, 100, 200, 500, 1000`; datas em
ISO-8601. **(obrig.)** = obrigatório.

---

## Endpoints

### `GET /v1/venda/busca` — listar/filtrar
Sem obrigatórios. Principais filtros (query): `pagina`, `tamanho_pagina`,
`termo_busca`, `data_inicio`/`data_fim`, `data_criacao_de`/`_ate`,
`data_alteracao_de`/`_ate`, `ids_vendedores`, `ids_clientes`, `ids_produtos`,
`ids_categorias`, `situacoes`, `tipos`, `origens`, `numeros`, `pendente`,
`totais`. Ordenação por `NUMERO` \| `CLIENTE` \| `DATA`.

### `POST /v1/venda` — criar
Body: `CriacaoVendaRequest` (abaixo).

### `GET /v1/venda/{id}` — detalhar
Path: `id` **(obrig.)**.

### `PUT /v1/venda/{id}` — atualizar
Path: `id` **(obrig.)**. Body: `VendaParaEdicaoRequest`.

### `GET /v1/venda/{id}/itens` — itens da venda
Path: `id_venda` **(obrig.)**. Paginação por `pagina`/`tamanho_pagina`.

### `GET /v1/venda/{id}/imprimir` — PDF da venda
Path: `id` **(obrig.)**. Retorna o PDF.

### `GET /v1/venda/proximo-numero` — próximo número de venda
### `GET /v1/venda/vendedores` — listar vendedores
### `POST /v1/venda/exclusao-lote` — excluir em lote
Body: `ExclusaoLote` → `{ "ids": ["<uuid>", ...] }`.

---

## Schema: CriacaoVendaRequest

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_cliente`* | string | Cliente |
| `numero`* | integer | Número da venda (ver `proximo-numero`) |
| `situacao`* | enum | `EM_ANDAMENTO` \| `APROVADO` |
| `data_venda`* | string | ISO |
| `itens`* | array<ItemVendaRequest> | Itens |
| `condicao_pagamento`* | CondicaoPagamentoRequest | Pagamento |
| `id_categoria` | string | Categoria |
| `id_centro_custo` | string | Centro de custo |
| `id_vendedor` | string | Vendedor |
| `composicao_de_valor` | objeto | `frete` + `desconto` |
| `observacoes` / `observacoes_pagamento` | string | |

### ItemVendaRequest
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id`* | string | ID do produto/serviço |
| `quantidade`* | number | |
| `valor`* | number | Valor unitário |
| `descricao` | string | |
| `valor_custo` | number | |
| `itens_kit` | array | Itens de kit (se aplicável) |

### CondicaoPagamentoRequest
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `opcao_condicao_pagamento`* | string | Condição (ex.: à vista, parcelado) |
| `parcelas`* | array<ParcelaRequest> | Parcelas |
| `tipo_pagamento` | enum | ver `TipoDePagamento` (lista abaixo) |
| `id_conta_financeira` | string | Conta financeira |
| `nsu` | string | NSU |

### Exemplo mínimo
```json
{
  "id_cliente": "<uuid>",
  "numero": 1,
  "situacao": "EM_ANDAMENTO",
  "data_venda": "2026-06-19",
  "itens": [{ "id": "<uuid_produto>", "quantidade": 1, "valor": 100.0 }],
  "condicao_pagamento": {
    "opcao_condicao_pagamento": "À vista",
    "parcelas": [{ "valor": 100.0, "data_vencimento": "2026-06-19" }]
  }
}
```

---

## Enums

- **situacao** (na criação): `EM_ANDAMENTO`, `APROVADO`.
- **Status** (filtro `situacoes`): `REVISAO_PENDENTE`, `EM_ORCAMENTO`,
  `ORCAMENTO_ACEITO`, `ORCAMENTO_RECUSADO`, `EM_ANDAMENTO`, `CONTRATO`,
  `CANCELADO`, `PREVISAO`, `INCOMPLETA`.
- **TipoOperacao**: `VENDA`, `REMESSA`, `COMPRA`, `DEVOLUCAO`.
- **tipo_pagamento**: `BOLETO_BANCARIO`, `CARTAO_CREDITO`, `CARTAO_DEBITO`,
  `CARTEIRA_DIGITAL`, `CASHBACK`, `CHEQUE`, `CREDITO_LOJA`, `CREDITO_VIRTUAL`,
  `DEPOSITO_BANCARIO`, `DINHEIRO`, `OUTRO`, `DEBITO_AUTOMATICO`,
  `CARTAO_CREDITO_VIA_LINK`, `PIX_PAGAMENTO_INSTANTANEO`, `PIX_COBRANCA`,
  `PROGRAMA_FIDELIDADE`, `SEM_PAGAMENTO`, `TRANSFERENCIA_BANCARIA`,
  `VALE_ALIMENTACAO`, `VALE_COMBUSTIVEL`, `VALE_PRESENTE`, `VALE_REFEICAO`.
- **TipoDesconto**: `PORCENTAGEM`, `VALOR`.

> Fonte: <https://developers.contaazul.com/docs/sales-apis-openapi/v1>
