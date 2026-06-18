# Conta Azul — Financial API Skill

Claude Agent Skill for the [Conta Azul Financial API (v1)](https://developers.contaazul.com/docs/financial-apis-openapi/v1):
accounts payable and receivable, installments, cost centers, categories,
financial accounts, balances and transfers — including the OAuth 2.0
authentication flow.

## Layout

```
SKILL.md              # skill instructions (overview, endpoints, business rules)
references/           # authentication, endpoints, schemas and common errors
scripts/ca_client.py  # Python client (stdlib only): OAuth + API calls
.env.example          # credentials template (copy to .env)
```

## Setup

1. Create an app in the [Developer Portal](https://developers.contaazul.com) and
   note the `client_id`, `client_secret` and the registered `redirect_uri`.
2. Copy the template and fill it in:
   ```bash
   cp .env.example .env   # edit with your values
   ```
3. Authenticate once (OAuth Authorization Code flow):
   ```bash
   python3 scripts/ca_client.py authorize-url   # open the URL, sign in with an ERP account
   python3 scripts/ca_client.py exchange --code CODE_FROM_REDIRECT
   ```
   This creates `token.json` (mode `0600`). From then on the token refreshes
   itself automatically.

## Usage

```bash
python3 scripts/ca_client.py get /v1/conta-financeira --query pagina=1 tamanho_pagina=50
python3 scripts/ca_client.py post /v1/centro-de-custo --body '{"nome":"Marketing"}'
```

## Security

`.env` (secrets) and `token.json` (tokens) are **not** versioned — see
`.gitignore`. The `refresh_token` rotates on every renewal and is rewritten
automatically; use the token in a single place so it is not invalidated.

> The skill instructions and reference docs (`SKILL.md`, `references/`) are
> written in Portuguese, matching the Conta Azul (Brazilian) API.
