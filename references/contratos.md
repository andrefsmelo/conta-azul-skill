# API de Contratos (Vendas Agendadas / Recorrência) — v1

Outra API da Conta Azul (`open-api-scheduled-sales`), **mesmo host e mesma
autenticação** do Financeiro: `https://api-v2.contaazul.com`, header
`Authorization: Bearer <token>`. O `scripts/ca_client.py` chama estes endpoints
sem alteração.

Gerencia **contratos de venda recorrente** (assinaturas): criação, consulta,
encerramento e remoção. Cada contrato gera vendas agendadas conforme os termos
de recorrência.

Convenções: `tamanho_pagina` (paginação), datas em ISO-8601. **(obrig.)** =
obrigatório.

---

## Endpoints

### `GET /v1/contratos` — listar
| Param | Tipo | Notas |
| --- | --- | --- |
| `data_inicio` **(obrig.)** | string | ISO |
| `data_fim` **(obrig.)** | string | ISO |
| `pagina` | integer | |
| `tamanho_pagina` | integer | |
| `busca_textual` | string | |
| `cliente_id` | array | filtra por cliente(s) |
| `tipo_pagamento` | array | ver `TipoDePagamento` |
| `status` | string | `TODOS` \| `ATIVO` \| `INATIVO` \| `PROXIMO_AO_VENCIMENTO` |
| `campo_ordenado_ascendente` / `_descendente` | string | `DATA_INICIO` \| `DATA_FIM` |

### `POST /v1/contratos` — criar
Body: `CriarContrato` (abaixo).

### `GET /v1/contratos/proximo-numero` — próximo número de contrato
Sem parâmetros. Retorna o número sugerido para o próximo contrato.

### `GET /v1/contratos/{id}` — detalhar
Path: `id` **(obrig.)**.

### `DELETE /v1/contratos/{id}` — remover
Path: `id` **(obrig.)**. Exclui **permanentemente**, cancelando todas as vendas
associadas (agendadas e efetivadas). Contratos em reajuste de valor não podem
ser removidos.

### `POST /v1/contratos/{id}/encerrar` — encerrar
Path: `id` **(obrig.)**. Desativa o contrato (não gera novas cobranças).
Contratos em reajuste de valor não podem ser encerrados.

---

## Schema: CriarContrato

Campos com `*` são obrigatórios.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_cliente`* | string | Cliente do contrato |
| `itens`* | array<CriarItemVendaContrato> | Itens (produtos/serviços) |
| `condicao_pagamento`* | CriarCondicaoPagamentoContrato | Pagamento |
| `termos`* | CriarTermosContrato | Recorrência |
| `composicao_de_valor` | CriarComposicaoValorContrato | Frete e desconto |
| `id_categoria` | string | Categoria |
| `id_centro_custo` | string | Centro de custo |
| `id_vendedor` | string | Vendedor responsável |
| `observacoes` | string | Observações gerais |
| `observacoes_pagamento` | string | Observações p/ nota fiscal |

### CriarItemVendaContrato
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id`* | string | ID do item (produto/serviço) |
| `quantidade`* | number | Quantidade |
| `valor`* | number | Valor unitário |
| `descricao` | string | Descrição |
| `valor_custo` | number | Custo |

### CriarCondicaoPagamentoContrato
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `tipo_pagamento`* | enum | ver `TipoDePagamento` |
| `dia_vencimento`* | integer | Dia do mês de vencimento |
| `primeira_data_vencimento`* | string | ISO |
| `id_conta_financeira` | string | Conta financeira |

### CriarTermosContrato (recorrência)
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `numero`* | integer | Número do contrato |
| `data_inicio`* | string | ISO |
| `data_fim`* | string | ISO |
| `dia_emissao_venda`* | integer | Dia de emissão de cada venda |
| `tipo_frequencia`* | enum | `MENSAL` \| `ANUAL` |
| `intervalo_frequencia`* | integer | A cada N períodos |
| `tipo_expiracao`* | enum | `DATA` \| `NUNCA` |

### CriarComposicaoValorContrato
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `frete` | number | Valor do frete |
| `desconto.tipo`* | enum | `PORCENTAGEM` \| `VALOR` |
| `desconto.valor`* | number | Valor/percentual do desconto |

---

## Enums

- **TipoDePagamento**: `BOLETO_BANCARIO`, `CARTAO_CREDITO`, `CARTAO_DEBITO`,
  `CARTEIRA_DIGITAL`, `CASHBACK`, `CHEQUE`, `CREDITO_LOJA`, `CREDITO_VIRTUAL`,
  `DEPOSITO_BANCARIO`, `DINHEIRO`, `OUTRO`, `DEBITO_AUTOMATICO`,
  `LINK_PAGAMENTO`, `PIX_PAGAMENTO_INSTANTANEO`, `COBRANCA_PIX`,
  `PROGRAMA_FIDELIDADE`, `SEM_PAGAMENTO`, `TRANSFERENCIA_BANCARIA`,
  `VALE_ALIMENTACAO`, `VALE_COMBUSTIVEL`, `VALE_PRESENTE`, `VALE_REFEICAO`.
- **TipoFrequenciaRecorrencia**: `MENSAL`, `ANUAL`.
- **TipoExpiracaoRecorrencia**: `DATA`, `NUNCA`.
- **TipoDeDesconto**: `PORCENTAGEM`, `VALOR`.

> Fonte: <https://developers.contaazul.com/docs/open-api-scheduled-sales/v1>
