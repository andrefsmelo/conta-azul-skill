# API de Notas Fiscais — v1

API da Conta Azul (`open-api-invoice`), **mesmo host e mesma autenticação**:
`https://api-v2.contaazul.com`, header `Authorization: Bearer <token>`. O
`scripts/ca_client.py` chama estes endpoints sem alteração.

Consulta de **notas fiscais** (NF-e de produto e NFS-e de serviço) e vínculo de
notas a um **MDF-e** (manifesto de documentos fiscais).

Convenções: `tamanho_pagina` aqui aceita apenas `10, 20, 50, 100`; datas em
ISO-8601. **(obrig.)** = obrigatório.

> ⚠️ **Janela máxima de 15 dias** (verificado em chamada real): nas listagens, o
> intervalo entre as datas (`data_inicial`/`data_final` ou
> `data_competencia_de`/`_ate`) **não pode passar de 15 dias** — senão retorna
> `HTTP 400`. Para períodos maiores, pagine por janelas de até 15 dias.
>
> **Envelope de resposta:** `{ "itens": [...], "paginacao": { "pagina_atual",
> "total_paginas", "tamanho_pagina", "total_itens" } }` — diferente das outras
> APIs (o total fica em `paginacao.total_itens`).

---

## Endpoints

### `GET /v1/notas-fiscais` — listar NF-e (produto) por filtro
| Param | Tipo | Notas |
| --- | --- | --- |
| `data_inicial` **(obrig.)** | string | ISO |
| `data_final` **(obrig.)** | string | ISO |
| `pagina` / `tamanho_pagina` | integer | `10\|20\|50\|100` |
| `documento_tomador` | string | CPF/CNPJ do tomador |
| `numero_nota` | string | |
| `id_venda` | string | |

### `GET /v1/notas-fiscais-servico` — listar NFS-e (serviço) por filtro
| Param | Tipo | Notas |
| --- | --- | --- |
| `data_competencia_de` **(obrig.)** | string | ISO |
| `data_competencia_ate` **(obrig.)** | string | ISO |
| `pagina` / `tamanho_pagina` | integer | `10\|20\|50\|100` |
| `ids` / `id_cliente` | array | |
| `numero_venda` | integer | |
| `numero_nfse_inicial` / `_final` | integer | faixa de número da NFS-e |
| `numero_rps_inicial` / `_final` | integer | faixa de RPS |
| `status` | array | ver `StatusNotaFiscalServico` |
| `tipo_negociacao` | string | `VENDA` \| `CONTRATO` |

### `GET /v1/notas-fiscais/{chave}` — detalhar por chave de acesso
Path: `chave` **(obrig.)** — chave de acesso da nota.

### `POST /v1/notas-fiscais/vinculo-mdfe` — vincular notas a um MDF-e
Body: `LinkNotaFiscalMdfe`:
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `identificador`* | string | Identificador do MDF-e |
| `chaves_acesso`* | array<string> | Chaves de acesso das notas a vincular |
| `status` | enum | Status do MDF-e (ver `StatusDoMDFE`) |

---

## Enums

- **StatusNotaFiscalServico** (NFS-e): `PENDENTE`, `PRONTA_ENVIO`,
  `AGUARDANDO_RETORNO`, `EM_ESPERA`, `EMITINDO`, `EMITIDA`, `CANCELADA`,
  `FALHA`, `FALHA_CANCELAMENTO`, `CORRIGIDA_SUCESSO`, `AGUARDANDO_CORRECAO`,
  `FALHA_CORRECAO`, `DENEGADA`, `CANCELAMENTO_MANUAL`.
- **StatusDaNotaFiscal** (NF-e): `EMITIDA`, `CORRIGIDA_SUCESSO`.
- **StatusDoMDFE**: `AUTORIZADO`, `ENCERRADO`, `CANCELADO`.

> Esta API é de **consulta** (não emite notas fiscais). O único `POST` é o
> vínculo de notas a um MDF-e.

> Fonte: <https://developers.contaazul.com/open-api-docs/open-api-invoice/v1>
