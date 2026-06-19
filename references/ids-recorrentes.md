# IDs recorrentes — AMBIENTE SANDBOX (desenvolvimento)

> ⚠️ **Apenas fixtures do ambiente de DESENVOLVIMENTO** (empresa de teste
> "Andre Melo", `...@devportal.com`). Servem para agilizar testes/exemplos sem
> precisar buscar por nome a cada POST.
>
> **NÃO coloque aqui UUIDs de clientes reais.** Eles são confidenciais e
> **por conta** — vão no `accounts.json`/`refs` do agente (gitignored), nunca
> num arquivo versionado da skill. Ver [multi-conta.md](multi-conta.md).
>
> UUIDs podem mudar/ser apagados no ERP — se um falhar, re-resolva via API.

Confirmados em chamadas reais a este sandbox:

| Recurso | Nome | ID |
| --- | --- | --- |
| Conta financeira | teste (CONTA_CORRENTE) | `56227ea5-d5ad-4e3d-9dca-8ffae5a9ca69` |
| Categoria (DESPESA) | Aluguel | `491de8c4-a6f5-42b5-a8db-11310d9f34d3` |
| Cliente / contato | Cliente 01 | `2964288e-2cd9-44d3-9c6a-b40c5226b881` |
| Vendedor | Andre Melo | `9386ba49-8267-4ab2-b4e3-2fd3b559f164` |
| Produto | Produto 01 | `b98aa9c1-4ee7-48b6-b179-f3afc5dff969` |
| Serviço | Serviço 01 | `3921731f-7204-4922-978c-3b90be4f9238` |
| Unidade de medida | Kilograma | `54448255` (inteiro) |
| Unidade de medida | Quantidade | `54448256` (inteiro) |

> Para descobrir IDs de outros recursos: `GET /v1/conta-financeira`,
> `GET /v1/categorias`, `GET /v1/pessoas`, `GET /v1/produtos`, `GET /v1/servicos`,
> `GET /v1/venda/vendedores`.
