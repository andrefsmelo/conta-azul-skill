# Endpoints da API Financeira (v1)

Base: `https://api-v2.contaazul.com` · Header: `Authorization: Bearer <token>`

Convenções:
- `tamanho_pagina` aceita apenas: `10, 20, 50, 100, 200, 500, 1000`.
- Datas em ISO-8601 (ex.: `2026-06-18` ou `2026-06-18T00:00:00`).
- Parâmetros marcados com **(obrig.)** são obrigatórios.

---

## Centros de custo

### `GET /v1/centro-de-custo` — listar
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` **(obrig.)** | number | |
| `tamanho_pagina` **(obrig.)** | number | enum de página |
| `busca` | string | busca textual |
| `filtro_rapido` | string | `ATIVO` \| `INATIVO` \| `TODOS` |
| `campo_ordenado_ascendente` | string | nome do campo |
| `campo_ordenado_descendente` | string | nome do campo |

### `POST /v1/centro-de-custo` — criar
Body: `CriacaoCentroDeCustoRequest` (ver schemas).

---

## Categorias

### `GET /v1/categorias` — listar
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` **(obrig.)** | number | |
| `tamanho_pagina` **(obrig.)** | number | enum de página |
| `permite_apenas_filhos` **(obrig.)** | boolean | |
| `tipo` | string | `RECEITA` \| `DESPESA` |
| `nome` | string | |
| `busca` | string | |
| `apenas_filhos` | boolean | |
| `campo_ordenado_ascendente` | string | `NOME` \| `TIPO` |
| `campo_ordenado_descendente` | string | `NOME` \| `TIPO` |

### `GET /v1/categorias/configuracao-padrao` — de-para de categorias
Retorna o de-para entre operações financeiras e categorias do tenant.
| Param | Tipo | Notas |
| --- | --- | --- |
| `sugestao_padrao` | boolean | inclui a sugestão padrão por operação |

### `GET /v1/financeiro/categorias-dre` — listar categorias DRE
Sem parâmetros. Estrutura contábil-financeira (DRE).

---

## Contas financeiras

### `GET /v1/conta-financeira` — listar
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` | integer | |
| `tamanho_pagina` | integer | enum de página |
| `tipos` | array | filtra por tipo de conta |
| `nome` | string | |
| `apenas_ativo` | boolean | |
| `esconde_conta_digital` | boolean | |
| `mostrar_caixinha` | boolean | |

### `GET /v1/conta-financeira/{id_conta_financeira}/saldo-atual` — saldo atual
Path: `id_conta_financeira` **(obrig.)**.

### `GET /v1/financeiro/eventos-financeiros/saldo-inicial` — saldos iniciais
| Param | Tipo | Notas |
| --- | --- | --- |
| `data_inicio` **(obrig.)** | string | ISO |
| `data_fim` **(obrig.)** | string | ISO |
| `pagina` | integer | |
| `tamanho_pagina` | integer | |

---

## Transferências

### `GET /v1/financeiro/transferencias` — listar
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` | integer | |
| `tamanho_pagina` | integer | enum de página |
| `ids_conta_financeira` | array | |
| `data_inicio` | string | ISO |
| `data_fim` | string | ISO |

---

## Eventos financeiros (contas a pagar / a receber)

### `POST /v1/financeiro/eventos-financeiros/contas-a-receber` — criar receita
Body: `EventoFinanceiroRequest` (ver schemas).

### `POST /v1/financeiro/eventos-financeiros/contas-a-pagar` — criar despesa
Body: `EventoFinanceiroRequest` (ver schemas).

### `GET /v1/financeiro/eventos-financeiros/contas-a-receber/buscar` — buscar receitas
### `GET /v1/financeiro/eventos-financeiros/contas-a-pagar/buscar` — buscar despesas
Mesmos parâmetros nas duas buscas:
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` **(obrig.)** | integer | |
| `tamanho_pagina` **(obrig.)** | integer | enum de página |
| `data_vencimento_de` **(obrig.)** | string | ISO |
| `data_vencimento_ate` **(obrig.)** | string | ISO |
| `descricao` | string | |
| `data_competencia_de` / `_ate` | string | ISO |
| `data_pagamento_de` / `_ate` | string | ISO |
| `data_alteracao_de` / `_ate` | string | ISO |
| `valor_de` / `valor_ate` | string | |
| `status` | array | situação das parcelas |
| `ids_contas_financeiras` | array | |
| `ids_categorias` | array | |
| `ids_centros_de_custo` | array | |
| `ids_clientes` | array | apenas em contas a receber |
| `campo_ordenado_ascendente` / `_descendente` | string | em contas a pagar: `ID` \| `CODIGO` \| `NOME` \| `ATIVO` |

### `GET /v1/financeiro/eventos-financeiros/{id_evento}/parcelas` — parcelas do evento
Path: `id_evento` **(obrig.)**. Lista as parcelas de um lançamento.

### `GET /v1/financeiro/eventos-financeiros/parcelas/{id}` — parcela por id
Path: `id` **(obrig.)**. Detalhes de uma parcela (a pagar ou a receber):
vencimento, valor, status, conta financeira, rateio, categoria, centro de custo.

### `PATCH /v1/financeiro/eventos-financeiros/parcelas/{id}` — atualizar parcela
Path: `id` **(obrig.)**. Body: `ParcelaAtualizacaoRequest` (ver schemas).
Atualização **parcial**; `versao` é obrigatória (concorrência otimista).

### `GET /v1/financeiro/eventos-financeiros/alteracoes` — eventos alterados
Retorna os **IDs** de eventos (a pagar e a receber) alterados num período.
| Param | Tipo | Notas |
| --- | --- | --- |
| `data_inicio` **(obrig.)** | string | ISO |
| `data_fim` **(obrig.)** | string | ISO |
| `pagina` | integer | |
| `tamanho_pagina` | integer | |

> Indica a data/hora em que o evento foi salvo, **sem** detalhar quais campos
> mudaram. Salvar sem alteração real pode gerar entrada no histórico.
