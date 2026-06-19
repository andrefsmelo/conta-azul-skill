---
name: conta-azul-skill
description: >-
  Integração com as APIs (v1) da Conta Azul (ERP brasileiro) — todas no mesmo
  host (api-v2.contaazul.com) e mesma autenticação OAuth 2.0. Use ao criar,
  consultar ou atualizar: contas a pagar/receber, parcelas, centros de custo,
  categorias, contas financeiras, saldos e transferências (Financeiro); clientes,
  fornecedores e transportadoras (Pessoas); produtos e estoque (Produtos);
  vendas e itens (Vendas); orçamentos/propostas (Orçamentos); contratos de
  recorrência (Contratos); serviços (Serviços); notas fiscais NF-e/NFS-e (Notas
  Fiscais); status de operações assíncronas (Protocolos). Também para a
  autenticação OAuth 2.0 (Authorization Code): troca de código por token e
  renovação de access_token via refresh_token.
---

# Conta Azul — APIs v1 (Financeiro, Pessoas, Produtos, Vendas e mais)

Skill para integrar com a Conta Azul. Cobre o fluxo de autenticação OAuth 2.0 e
nove APIs (todas no mesmo host e mesma autenticação):

- **Financeiro**: eventos (contas a pagar/a receber), parcelas, centros de
  custo, categorias, categorias DRE, contas financeiras, saldos e transferências.
- **Contratos** (vendas agendadas/recorrência): listar, criar, detalhar,
  encerrar e remover contratos — ver [references/contratos.md](references/contratos.md).
- **Pessoas**: clientes, fornecedores e transportadoras (criar, consultar,
  atualizar, ativar/inativar/excluir em lote) — ver [references/pessoas.md](references/pessoas.md).
- **Produtos** (estoque): catálogo de produtos, estoque, fiscal, kits/variações
  e tabelas auxiliares (NCM, CEST, unidades) — ver [references/produtos.md](references/produtos.md).
- **Notas fiscais** (consulta): NF-e e NFS-e por filtro, detalhe por chave e
  vínculo a MDF-e — ver [references/notas-fiscais.md](references/notas-fiscais.md).
- **Serviços**: catálogo de serviços (criar, consultar, atualizar, excluir em
  lote) — ver [references/servicos.md](references/servicos.md).
- **Vendas**: vendas/orçamentos (criar, consultar, editar, itens, PDF,
  vendedores, exclusão em lote) — ver [references/vendas.md](references/vendas.md).
- **Orçamentos** (propostas): criar, consultar e excluir em lote — ver
  [references/orcamentos.md](references/orcamentos.md).

## URLs base

| Finalidade | Host |
| --- | --- |
| Autenticação (login, token, refresh) | `https://auth.contaazul.com` |
| Chamadas à API (recursos) | `https://api-v2.contaazul.com` |

Toda chamada à API leva o cabeçalho `Authorization: Bearer <access_token>`.

## Autenticação (resumo)

OAuth 2.0 **Authorization Code**. Quatro etapas:

1. **Solicitar código** — redirecionar o usuário para
   `https://auth.contaazul.com/login?response_type=code&client_id=...&redirect_uri=...&state=...&scope=openid+profile+aws.cognito.signin.user.admin`.
   Após autorizar, a Conta Azul redireciona para `redirect_uri?code=...&state=...`.
2. **Trocar código por token** — `POST https://auth.contaazul.com/oauth2/token`
   com `grant_type=authorization_code`, `code`, `redirect_uri` e header
   `Authorization: Basic base64(client_id:client_secret)`.
3. **Renovar token** — mesmo endpoint com `grant_type=refresh_token`. O
   `access_token` expira em **1 hora**; **salve sempre o novo `refresh_token`**,
   pois ele muda a cada renovação.
4. **Chamar a API** — usar `Authorization: Bearer <access_token>`.

Detalhes completos (parâmetros, exemplos de cURL, validade dos tokens) em
[references/autenticacao.md](references/autenticacao.md).

## Endpoints (referência rápida)

Base: `https://api-v2.contaazul.com`

| Recurso | Método e caminho |
| --- | --- |
| Listar centros de custo | `GET /v1/centro-de-custo` |
| Criar centro de custo | `POST /v1/centro-de-custo` |
| Listar categorias | `GET /v1/categorias` |
| Config. padrão de categorias | `GET /v1/categorias/configuracao-padrao` |
| Listar categorias DRE | `GET /v1/financeiro/categorias-dre` |
| Listar contas financeiras | `GET /v1/conta-financeira` |
| Saldo atual da conta | `GET /v1/conta-financeira/{id_conta_financeira}/saldo-atual` |
| Saldos iniciais | `GET /v1/financeiro/eventos-financeiros/saldo-inicial` |
| Listar transferências | `GET /v1/financeiro/transferencias` |
| Criar conta a receber | `POST /v1/financeiro/eventos-financeiros/contas-a-receber` |
| Buscar receitas (parcelas) | `GET /v1/financeiro/eventos-financeiros/contas-a-receber/buscar` |
| Criar conta a pagar | `POST /v1/financeiro/eventos-financeiros/contas-a-pagar` |
| Buscar despesas (parcelas) | `GET /v1/financeiro/eventos-financeiros/contas-a-pagar/buscar` |
| Parcelas de um evento | `GET /v1/financeiro/eventos-financeiros/{id_evento}/parcelas` |
| Parcela por id | `GET /v1/financeiro/eventos-financeiros/parcelas/{id}` |
| Atualizar parcela (parcial) | `PATCH /v1/financeiro/eventos-financeiros/parcelas/{id}` |
| Eventos alterados num período | `GET /v1/financeiro/eventos-financeiros/alteracoes` |
| Status de protocolo (confirma criação) | `GET /v1/protocolo/{id}` *(ver [references/protocolos.md](references/protocolos.md))* |

### Contratos (vendas recorrentes) — ver [references/contratos.md](references/contratos.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar contratos | `GET /v1/contratos` |
| Criar contrato | `POST /v1/contratos` |
| Próximo número de contrato | `GET /v1/contratos/proximo-numero` |
| Detalhar contrato | `GET /v1/contratos/{id}` |
| Encerrar contrato | `POST /v1/contratos/{id}/encerrar` |
| Remover contrato | `DELETE /v1/contratos/{id}` |

### Pessoas (clientes/fornecedores/transportadoras) — ver [references/pessoas.md](references/pessoas.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar/filtrar pessoas | `GET /v1/pessoas` |
| Criar pessoa | `POST /v1/pessoas` |
| Detalhar pessoa | `GET /v1/pessoas/{id}` |
| Atualizar (completo / parcial) | `PUT` / `PATCH /v1/pessoas/{id}` |
| Empresa conectada ao token | `GET /v1/pessoas/conta-conectada` |
| Ativar / inativar / excluir em lote | `POST /v1/pessoas/{ativar\|inativar\|excluir}` |

### Produtos (estoque) — ver [references/produtos.md](references/produtos.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar/filtrar produtos | `GET /v1/produtos` |
| Criar produto | `POST /v1/produtos` |
| Detalhar produto | `GET /v1/produtos/{id}` |
| Atualizar (parcial) | `PATCH /v1/produtos/{id}` |
| Remover produto | `DELETE /v1/produtos/{id}` |
| Tabelas auxiliares | `GET /v1/produtos/{categorias\|ncm\|cest\|unidades-medida\|ecommerce-categorias\|ecommerce-marcas}` |

### Notas fiscais (consulta) — ver [references/notas-fiscais.md](references/notas-fiscais.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar NF-e (produto) | `GET /v1/notas-fiscais` |
| Listar NFS-e (serviço) | `GET /v1/notas-fiscais-servico` |
| Detalhar por chave | `GET /v1/notas-fiscais/{chave}` |
| Vincular notas a MDF-e | `POST /v1/notas-fiscais/vinculo-mdfe` |

### Serviços — ver [references/servicos.md](references/servicos.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar/filtrar serviços | `GET /v1/servicos` |
| Criar serviço | `POST /v1/servicos` |
| Detalhar serviço | `GET /v1/servicos/{id}` |
| Atualizar (parcial) | `PATCH /v1/servicos/{id}` |
| Excluir em lote (com corpo) | `DELETE /v1/servicos` |

### Vendas — ver [references/vendas.md](references/vendas.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar/filtrar vendas | `GET /v1/venda/busca` |
| Criar venda | `POST /v1/venda` |
| Detalhar / editar venda | `GET` / `PUT /v1/venda/{id}` |
| Itens da venda | `GET /v1/venda/{id}/itens` |
| PDF da venda | `GET /v1/venda/{id}/imprimir` |
| Próximo número / vendedores | `GET /v1/venda/proximo-numero` · `GET /v1/venda/vendedores` |
| Excluir em lote | `POST /v1/venda/exclusao-lote` |

### Orçamentos (propostas) — ver [references/orcamentos.md](references/orcamentos.md)

| Recurso | Método e caminho |
| --- | --- |
| Listar/filtrar orçamentos | `GET /v1/orcamentos` |
| Criar orçamento | `POST /v1/orcamentos` |
| Detalhar orçamento | `GET /v1/orcamentos/{id}` |
| Excluir em lote (com corpo) | `DELETE /v1/orcamentos` |

Parâmetros de query e detalhes dos endpoints do **Financeiro** em
[references/endpoints.md](references/endpoints.md); schemas dos corpos do
Financeiro em [references/schemas.md](references/schemas.md). As demais APIs têm
seus endpoints e schemas na respectiva referência (links acima). O cliente
suporta `GET`, `POST`, `PUT`, `PATCH` e `DELETE` (este com ou sem corpo).

## Cliente auxiliar

[scripts/ca_client.py](scripts/ca_client.py) é um cliente Python (somente
biblioteca padrão) que cuida do `Basic auth`, da renovação automática do token e
das chamadas à API. Os segredos estáticos ficam no `.env` na **raiz do agent**
(o cliente sobe a árvore de diretórios para encontrá-lo); os tokens são
persistidos em `token.json` **ao lado do `.env`** (permissão `0600`, fora do
versionamento) e o `refresh_token` rotacionado é regravado automaticamente a
cada renovação.

`.env` (na raiz do agent — apenas segredos estáticos):
```
CLIENT_ID=...
CLIENT_SECRET=...
REDIRECT_URI=...        # idêntica à cadastrada no Portal do Desenvolvedor
```

Fluxo inicial (uma vez) e uso:
```bash
python scripts/ca_client.py authorize-url          # abra a URL no navegador...
# ...logue com uma conta do ERP (NÃO a do Portal do Desenvolvedor),
# copie o ?code=... do redirect e troque por tokens:
python scripts/ca_client.py exchange --code SEU_CODE
# daqui em diante as chamadas se autenticam/renovam sozinhas:
python scripts/ca_client.py get /v1/conta-financeira --query pagina=1 tamanho_pagina=50
```

> Na tela de autorização use **uma conta do ERP**, não a conta do Portal do
> Desenvolvedor — senão a API responde `401` mesmo com o token válido.

**Multi-conta (vários ERPs):** passe `--token-file <caminho>` em cada comando
para usar o token de uma conta específica. A skill é stateless quanto a contas —
quem decide o caminho por conta/grupo é o agente. Direcionamentos para o agente
organizar seu `accounts.json` em [references/multi-conta.md](references/multi-conta.md).

## Criação de eventos é assíncrona (protocolo)

`POST` de contas a pagar/receber **não cria o evento na hora**. A resposta é um
**protocolo** com `status: PENDING`:

```json
{ "protocolo": "71145dda-...", "status": "PENDING", "data_criacao": "..." }
```

O processamento (e a validação das referências, como `conta_financeira`) ocorre
depois. Consulte o desfecho real em `GET /v1/protocolo/{id}` (API de Protocolos,
host `api-v2.contaazul.com`):

```json
{ "status": "SUCCESS", "evento_financeiro_id": "1be7796e-...",
  "resposta": "O evento financeiro foi criado no contas a pagar..." }
```

Se `status: ERROR`, o campo `resposta` traz o motivo (ex.: *"A conta financeira
de id ... não existe."*). Sempre confira o protocolo antes de assumir sucesso —
um `200` no POST só significa que foi **enfileirado**. Detalhes do recurso de
protocolo em [references/protocolos.md](references/protocolos.md).

## Regras de negócio importantes

- **`conta_financeira` deve existir no ERP**: não há `POST /v1/conta-financeira`
  nesta API — contas financeiras (banco, caixa, cartão) são criadas no próprio
  ERP. Liste-as com `GET /v1/conta-financeira` para obter um ID válido.
- **`rateio` é obrigatório na criação**: ao menos uma categoria
  (`id_categoria`). Use `GET /v1/categorias?tipo=DESPESA` (ou `RECEITA`) com
  `apenas_filhos=true` para pegar categorias que aceitam lançamento.
- **`detalhe_valor` da parcela exige `valor_liquido`** além de `valor_bruto`.
- **IDs recorrentes**: para acelerar testes no sandbox, IDs comuns (conta
  financeira, categoria, cliente…) estão em
  [references/ids-recorrentes.md](references/ids-recorrentes.md). Para cliente
  real, use o cache `refs` por conta (ver [references/multi-conta.md](references/multi-conta.md)).
- **Paginação**: `tamanho_pagina` só aceita `10, 20, 50, 100, 200, 500, 1000`.
- **Datas**: use ISO-8601. Buscas de parcelas exigem `data_vencimento_de` e
  `data_vencimento_ate` obrigatórios.
- **Rateio**: ao criar um evento, a soma dos valores do `rateio` (por categoria)
  e da `condicao_pagamento` (parcelas) deve bater com o `valor` do evento.
- **Atualização de parcela** (`PATCH`): é obrigatório enviar `versao` com o
  valor atual da parcela (controle de concorrência otimista).
- **Rate limits**: 600 chamadas/minuto e até 10/segundo por conta ERP conectada.
  Em `429`, aplique backoff exponencial.

## Erros comuns

| Erro | Causa provável | Ação |
| --- | --- | --- |
| `invalid_grant` | `code`/`refresh_token` inválido, expirado ou já usado; `redirect_uri`/`client_id` divergente | Refazer o fluxo OAuth; conferir `redirect_uri` idêntico ao cadastrado |
| `401 Unauthorized` | `access_token` ausente, inválido ou expirado | Renovar o token com `refresh_token` |
| `429 Too Many Requests` | Excedeu o rate limit | Backoff exponencial; cache |
| `500 Internal Server Error` | Erro no servidor ou corpo malformado | Validar JSON/dados; reenviar após alguns segundos |

Mais detalhes em [references/erros-comuns.md](references/erros-comuns.md).

## Fontes

Documentação oficial da Conta Azul (<https://developers.contaazul.com>):

- Autenticação: <https://developers.contaazul.com/auth>
- Financeiro: <https://developers.contaazul.com/docs/financial-apis-openapi/v1>
- Contratos: <https://developers.contaazul.com/docs/open-api-scheduled-sales/v1>
- Pessoas: <https://developers.contaazul.com/open-api-docs/open-api-person/v1>
- Produtos: <https://developers.contaazul.com/open-api-docs/open-api-inventory/v1>
- Vendas: <https://developers.contaazul.com/docs/sales-apis-openapi/v1>
- Orçamentos: <https://developers.contaazul.com/docs/open-api-proposal/v1>
- Serviços: <https://developers.contaazul.com/open-api-docs/open-api-service/v1>
- Notas fiscais: <https://developers.contaazul.com/open-api-docs/open-api-invoice/v1>
- Protocolos: <https://developers.contaazul.com/docs/protocol-apis-openapi/v1>
- Erros comuns: <https://developers.contaazul.com/commonmistakes>
