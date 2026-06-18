# Schemas de request body

Campos com `*` são obrigatórios. `**` = a spec OpenAPI marca como opcional, mas
a API **rejeita a criação sem ele** (verificado em chamada real). Valores
monetários são `number`; datas em ISO-8601.

---

## EventoFinanceiroRequest
Usado em `POST .../contas-a-receber` e `POST .../contas-a-pagar`.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `data_competencia`* | string | Data de competência do evento |
| `valor`* | number | Valor total do evento |
| `observacao`* | string | Observação |
| `descricao`* | string | Descrição |
| `contato`* | string | Identificador do negociador/contato (cliente ou fornecedor) |
| `conta_financeira`* | string | Identificador da conta financeira |
| `rateio`** | array<CategoriaRateio> | Distribuição por categoria — exige ≥1 item na criação |
| `condicao_pagamento`* | ListaCondicaoPagamento | Parcelas |

### CategoriaRateio
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_categoria`* | string | Categoria |
| `valor`* | number | Valor atribuído à categoria |
| `rateio_centro_custo` | array<CentroCustoRateio> | Rateio por centro de custo |

### CentroCustoRateio
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id_centro_custo` | string | Centro de custo |
| `valor` | number | Valor atribuído |

### ListaCondicaoPagamento
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `parcelas`* | array<ParcelaCondicaoPagamento> | Lista de parcelas |

### ParcelaCondicaoPagamento
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `descricao`* | string | Descrição da parcela |
| `data_vencimento`* | string | Vencimento |
| `nota`* | string | Nota adicional |
| `conta_financeira`* | string | Conta financeira da parcela |
| `detalhe_valor`* | ComposicaoValor | Composição do valor |
| `metodo_pagamento` | string (enum) | Ver MetodoPagamento |

### Exemplo
```json
{
  "data_competencia": "2026-06-18",
  "valor": 1500.00,
  "observacao": "Pedido #1234",
  "descricao": "Venda de serviços",
  "contato": "ID_DO_CONTATO",
  "conta_financeira": "ID_DA_CONTA",
  "rateio": [
    {
      "id_categoria": "ID_CATEGORIA",
      "valor": 1500.00,
      "rateio_centro_custo": [
        { "id_centro_custo": "ID_CC", "valor": 1500.00 }
      ]
    }
  ],
  "condicao_pagamento": {
    "parcelas": [
      {
        "descricao": "Parcela 1/1",
        "data_vencimento": "2026-07-18",
        "nota": "",
        "conta_financeira": "ID_DA_CONTA",
        "metodo_pagamento": "PIX_PAGAMENTO_INSTANTANEO",
        "detalhe_valor": { "valor_bruto": 1500.00, "valor_liquido": 1500.00 }
      }
    ]
  }
}
```

> A soma do `rateio` e a soma das parcelas devem igualar o `valor` do evento.

---

## CriacaoCentroDeCustoRequest
Usado em `POST /v1/centro-de-custo`.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `nome`* | string | Nome do centro de custo |
| `codigo` | string | Código |

```json
{ "nome": "Marketing", "codigo": "MKT-01" }
```

---

## ParcelaAtualizacaoRequest
Usado em `PATCH /v1/financeiro/eventos-financeiros/parcelas/{id}`. Parcial.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `versao`* | integer | **Sempre** enviar a versão atual da parcela |
| `nota` | string | |
| `descricao` | string | |
| `vencimento` | string | |
| `composicao_valor` | ComposicaoValor | |
| `data_pagamento_esperado` | string | |
| `metodo_pagamento` | string (enum) | Ver MetodoPagamento |
| `perda` | PerdaFinanceira | `{ data, valor }` |
| `nsu` | string | |
| `pagamento_agendado` | boolean | |
| `id_conta_financeira` | string | |

```json
{
  "versao": 3,
  "vencimento": "2026-08-01",
  "composicao_valor": { "valor_bruto": 1500.00, "desconto": 50.00 }
}
```

---

## ComposicaoValor
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `valor_bruto`* | number | Valor bruto |
| `valor_liquido`** | number | Valor líquido — obrigatório na criação de evento |
| `desconto` | number | Desconto |
| `multa` | number | Multa |
| `juros` | number | Juros |
| `taxa` | number | Taxa |

---

## MetodoPagamento (enum)
`DINHEIRO`, `CARTAO_CREDITO`, `BOLETO_BANCARIO`, `CARTAO_CREDITO_VIA_LINK`,
`CHEQUE`, `CARTAO_DEBITO`, `TRANSFERENCIA_BANCARIA`, `OUTRO`, `CARTEIRA_DIGITAL`,
`CASHBACK`, `CREDITO_LOJA`, `CREDITO_VIRTUAL`, `DEPOSITO_BANCARIO`,
`PIX_PAGAMENTO_INSTANTANEO`, `PROGRAMA_FIDELIDADE`, `SEM_PAGAMENTO`,
`VALE_ALIMENTACAO`, `VALE_COMBUSTIVEL`, `VALE_PRESENTE`, `VALE_REFEICAO`,
`PIX_COBRANCA`, `DEBITO_AUTOMATICO`.
