# Autenticação OAuth 2.0 — Conta Azul

Fluxo **Authorization Code**. Host de autenticação: `https://auth.contaazul.com`.

Credenciais (`client_id` e `client_secret`) são criadas no Portal do
Desenvolvedor. Em apps de **produção** você define a `redirect_uri`; em apps de
**desenvolvimento** a Conta Azul usa `https://www.contaazul.com` e fornece dados
fictícios para testes.

## Etapa 1 — Solicitar o código de autorização

Redirecione o usuário (no navegador) para:

```
https://auth.contaazul.com/login?response_type=code&client_id=SEU_CLIENT_ID&redirect_uri=SUA_URL_REDIRECIONAMENTO&state=ESTADO&scope=openid+profile+aws.cognito.signin.user.admin
```

| Parâmetro | Valor | Fixo? | Finalidade |
| --- | --- | --- | --- |
| `response_type` | `code` | Sim | Pede um código de autorização |
| `client_id` | do Portal do Desenvolvedor | Não | Identifica o app |
| `redirect_uri` | **exatamente** igual à cadastrada | Não | Para onde redirecionar após autorizar |
| `state` | valor aleatório e único | Não | Proteção contra CSRF; ecoado de volta |
| `scope` | `openid profile aws.cognito.signin.user.admin` | Sim | Permissões (admin) |

> Use uma conta válida do **ERP** na tela de autorização — não a conta do Portal
> do Desenvolvedor.

Após autorizar, a Conta Azul redireciona para:

```
https://SUA_URL_REDIRECIONAMENTO?code=CODIGO_AUTORIZACAO&state=ESTADO
```

Valide que o `state` retornado é igual ao enviado.

## Etapa 2 — Trocar o código por tokens

```bash
curl --location 'https://auth.contaazul.com/oauth2/token' \
  --header 'Authorization: Basic BASE64(SEU_CLIENT_ID:SEU_CLIENT_SECRET)' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'code=CODIGO_AUTORIZACAO' \
  --data-urlencode 'grant_type=authorization_code' \
  --data-urlencode 'redirect_uri=SUA_URL_REDIRECIONAMENTO'
```

Resposta:

```json
{
  "access_token": "ACCESS_TOKEN_GERADO",
  "expires_in": 3600,
  "refresh_token": "REFRESH_TOKEN_GERADO",
  "token_type": "Bearer"
}
```

| Token | Validade | Finalidade |
| --- | --- | --- |
| `access_token` | 3600 s (1 h) | Autentica chamadas à API |
| `refresh_token` | até 5 anos / até a próxima renovação | Renova o `access_token` |

Guarde ambos com segurança. O `Basic` é `base64("client_id:client_secret")`.

## Etapa 3 — Renovar o access_token

```bash
curl --location 'https://auth.contaazul.com/oauth2/token' \
  --header 'Authorization: Basic BASE64(SEU_CLIENT_ID:SEU_CLIENT_SECRET)' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'refresh_token=REFRESH_TOKEN_GERADO' \
  --data-urlencode 'grant_type=refresh_token'
```

Resposta traz **novo** `access_token` **e novo** `refresh_token`.

> ⚠️ A cada renovação o `refresh_token` muda. Sempre persista o novo valor,
> senão a próxima renovação falhará com `invalid_grant`.

## Etapa 4 — Chamar a API

```bash
curl -i -X GET 'https://api-v2.contaazul.com/v1/categorias' \
  -H 'Authorization: Bearer <ACCESS_TOKEN_GERADO>'
```

O `access_token` é informação sensível: nunca o exponha ao usuário final.
