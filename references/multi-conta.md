# Multi-conta (vários ERPs por grupo) — direcionamento para o agente

A skill é **stateless** quanto a contas: ela **não guarda** nenhum mapa de
clientes nem decide qual conta usar. Quem mantém esse contexto é **o agente**.
A skill só precisa receber, em cada chamada, **qual arquivo de token usar**
(`--token-file`). Assim um mesmo app (um `client_id`/`client_secret`) atende
vários ERPs, cada um com seu próprio token.

## Divisão de responsabilidades

```
"em qual grupo estou"  ──►  conta (account)  ──►  arquivo de token  ──►  skill
        (agente)              [accounts.json do AGENTE]              (--token-file)
```

| Responsabilidade | Dono |
| --- | --- |
| Saber o grupo da conversa e mapear grupo → conta | **Agente** |
| Guardar o `accounts.json` (grupo → conta → caminho do token) | **Agente** |
| Guardar/rotacionar o token de cada conta | Arquivo do agente; a skill só lê/grava o que for apontado |
| Autenticar e chamar a API com o token certo | **Skill** (`--token-file`) |

> A skill nunca lê o `accounts.json`. Ele é do agente. A skill recebe apenas o
> caminho do token via `--token-file`.

## `accounts.json` (modelo sugerido — fica com o AGENTE, fora da skill)

Indexado pelo identificador do **grupo** (o agente condiciona a conta pelo grupo
em que está):

```json
{
  "telegram:-1001234567890": {
    "empresa": "Empresa A LTDA",
    "cnpj": "12345678000190",
    "token_file": "/dados/conta-azul/tokens/empresaA.json"
  },
  "telegram:-1009876543210": {
    "empresa": "Empresa B ME",
    "cnpj": "98765432000110",
    "token_file": "/dados/conta-azul/tokens/empresaB.json"
  }
}
```

Recomendações:
- **Chave = grupo** (ex.: `telegram:<chat_id>`), já que o agente decide a conta
  pelo grupo. Um grupo → uma conta.
- `token_file` aponta para um arquivo **fora da pasta da skill** (ex.: um volume
  de dados do agente). Permissão `0600`.
- Guarde também algo estável da empresa (CNPJ/`conta-conectada`) para auditoria.

## Onboarding de uma conta nova (uma vez por grupo)

Use o parâmetro **`state`** do OAuth para amarrar o grupo à autorização:

```bash
# 1. gerar a URL já marcando o grupo no state
python scripts/ca_client.py authorize-url --state "telegram:-1001234567890"

# 2. (usuário autoriza com a conta do ERP; volta ?code=...&state=...)

# 3. trocar o code salvando no arquivo de token DAQUELA conta
python scripts/ca_client.py exchange --code CODE \
    --token-file /dados/conta-azul/tokens/empresaA.json

# 4. (opcional) confirmar de quem é a conta e registrar no accounts.json
python scripts/ca_client.py get /v1/pessoas/conta-conectada \
    --token-file /dados/conta-azul/tokens/empresaA.json
```

O agente então grava no seu `accounts.json`: `grupo → { empresa, token_file }`.

## Em tempo de execução (cada mensagem)

1. O agente identifica o **grupo** da conversa.
2. Procura no `accounts.json` o `token_file` daquele grupo.
3. Chama a skill passando esse caminho:

```bash
python scripts/ca_client.py get /v1/financeiro/eventos-financeiros/contas-a-pagar/buscar \
    --query pagina=1 tamanho_pagina=50 data_vencimento_de=2026-06-01 data_vencimento_ate=2026-06-15 \
    --token-file /dados/conta-azul/tokens/empresaA.json
```

A renovação e a **rotação do `refresh_token`** acontecem dentro daquele arquivo,
automaticamente — sem afetar as outras contas.

## Cache de UUIDs recorrentes (refs)

Para evitar "buscar por nome → pegar id" a cada operação, o agente pode manter um
cache de UUIDs recorrentes **por conta**, dentro do `accounts.json` (ou em um
`refs.json` ao lado). A skill **não** mantém esse cache — é dado do agente.

```json
{
  "telegram:-1001234567890": {
    "empresa": "Empresa A LTDA",
    "token_file": "/dados/conta-azul/tokens/empresaA.json",
    "refs": {
      "conta_financeira_padrao": "56227ea5-d5ad-4e3d-9dca-8ffae5a9ca69",
      "categoria_aluguel": "491de8c4-a6f5-42b5-a8db-11310d9f34d3",
      "cliente_principal": "2964288e-2cd9-44d3-9c6a-b40c5226b881"
    }
  }
}
```

Regras para o cache não virar fonte de bug:
- **Só cacheie UUIDs confirmados pela API.** Nunca invente/adivinhe um UUID — IDs
  inexistentes falham (ex.: a criação assíncrona retorna protocolo `ERROR`).
- **Trate como atalho, com fallback:** se um UUID em cache falhar (`404`/erro),
  **re-resolva via API** (GET por nome/filtro) e atualize o cache.
- **UUID é por conta** — nunca reaproveite o ref de uma empresa em outra.
- Opcional: TTL (revalidar periodicamente), pois recursos podem ser apagados ou
  renomeados no ERP.

## Segurança e versionamento

| Dado | É credencial? | Como tratar |
| --- | --- | --- |
| Token (`token_file`) | **Sim** | Arquivo próprio, permissão `0600`, **nunca** versionar |
| `accounts.json` / `refs` (UUIDs) | **Não** (um UUID sem token não faz nada) | Mas é **dado confidencial do cliente** → fora do versionamento, `0600` |
| `client_id` / `client_secret` (`.env`) | **Sim** | `.env`, `0600`, nunca versionar |

- **Mantenha `accounts.json` (e `refs.json`, `tokens/`) sempre no `.gitignore`.**
  O `.gitignore` desta skill já cobre esses nomes; garanta o mesmo no
  repositório/volume onde o **agente** guarda esses arquivos (eles vivem fora da
  skill).
- Permissões restritas: arquivos `0600`, diretório de tokens `0700`.
- O `accounts.json` guarda **caminhos** de token e **refs** — não o token em si;
  ainda assim, é confidencial.
- Antes de commitar no lado do agente, confira: `git status` não deve listar
  `accounts.json`, `refs.json`, `*.token.json` nem `tokens/`.

## Notas

- **App compartilhado:** `client_id`/`client_secret`/`redirect_uri` continuam no
  `.env` (um app só autoriza vários ERPs). Só o **token** é por conta.
- **Sem `--token-file`:** o cliente usa o token padrão (uso single-conta),
  mantendo retrocompatibilidade.
- **Um token por arquivo, um uso por vez:** não rode renovações concorrentes do
  mesmo `token_file` (a rotação invalidaria o token em uso). Grupos diferentes =
  arquivos diferentes = sem conflito.
- **1 pessoa em vários grupos / 1 empresa em vários grupos:** modele no
  `accounts.json` do agente; a skill não precisa saber.
