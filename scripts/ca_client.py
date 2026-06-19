#!/usr/bin/env python3
"""Cliente mínimo para as APIs (v1) da Conta Azul.

Genérico: autentica via OAuth 2.0 e chama qualquer endpoint de
`api-v2.contaazul.com` (Financeiro, Contratos, Pessoas, Produtos, Vendas,
Orçamentos, Serviços, Notas Fiscais, Protocolos). Usa apenas a biblioteca
padrão. Cuida do Basic auth na renovação do token, da troca de código por token
e das chamadas autenticadas à API.

O .env é procurado subindo a árvore de diretórios (normalmente fica na RAIZ DO
AGENT, acima da skill). Os tokens são persistidos em `token.json` ao lado do
.env (permissão 0600, fora do versionamento). O refresh_token é rotacionado pela
Conta Azul a cada renovação e regravado automaticamente; o access_token fica em
cache até expirar. Assim, basta autenticar uma vez (exchange) e as chamadas
seguintes se renovam sozinhas. O .env guarda apenas os segredos estáticos.

Configuração (no .env na raiz do agent, ou variáveis de ambiente):
  CLIENT_ID / CONTA_AZUL_CLIENT_ID          (obrigatório)
  CLIENT_SECRET / CONTA_AZUL_CLIENT_SECRET  (obrigatório)
  REDIRECT_URI / CONTA_AZUL_REDIRECT_URI    (para authorize-url e exchange;
      deve ser idêntica à cadastrada no Portal do Desenvolvedor)

Fluxo inicial (uma vez):
  python ca_client.py authorize-url        # abra a URL, logue com conta do ERP
  python ca_client.py exchange --code CODE  # salva os tokens no token.json

Exemplos de CLI:
  # Trocar o code do OAuth por tokens (etapa 2)
  python ca_client.py exchange --code SEU_CODE

  # Renovar o access_token (etapa 3)
  python ca_client.py refresh

  # Chamadas à API (renova o token automaticamente se necessário)
  python ca_client.py get /v1/conta-financeira --query pagina=1 tamanho_pagina=50
  python ca_client.py get /v1/conta-financeira/ID/saldo-atual
  python ca_client.py post /v1/centro-de-custo --body '{"nome":"Marketing"}'
  python ca_client.py patch /v1/financeiro/eventos-financeiros/parcelas/ID \
      --body '{"versao":3,"vencimento":"2026-08-01"}'

Uso como módulo:
  from ca_client import ContaAzulClient
  cli = ContaAzulClient.from_env()
  contas = cli.get("/v1/conta-financeira", query={"pagina": 1, "tamanho_pagina": 50})
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AUTH_BASE = "https://auth.contaazul.com"
API_BASE = "https://api-v2.contaazul.com"
TOKEN_URL = f"{AUTH_BASE}/oauth2/token"
LOGIN_URL = f"{AUTH_BASE}/login"
SCOPE = "openid profile aws.cognito.signin.user.admin"


# caminho do .env efetivamente carregado (definido por load_dotenv)
_ENV_FILE = None


def find_env_file():
    """Procura o .env subindo a árvore de diretórios.

    O .env costuma ficar na RAIZ DO AGENT, acima da pasta da skill. Por isso
    procuramos a partir do diretório de trabalho e do diretório deste script,
    subindo até a raiz do sistema, e retornamos o primeiro .env encontrado.
    """
    seen = []
    for base in (os.getcwd(), os.path.dirname(os.path.abspath(__file__))):
        d = base
        while True:
            if d not in seen:
                seen.append(d)
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    for d in seen:
        cand = os.path.join(d, ".env")
        if os.path.isfile(cand):
            return cand
    return None


def load_dotenv(path=None):
    """Carrega um .env para os.environ sem sobrescrever o que já existe.

    Aceita linhas `KEY=valor` e `export KEY=valor`. Sem dependências externas.
    Registra o caminho do .env em _ENV_FILE (usado para localizar o token.json).
    """
    global _ENV_FILE
    cand = path or find_env_file()
    if not cand or not os.path.isfile(cand):
        return None
    with open(cand) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.replace("export", "", 1).strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
    _ENV_FILE = cand
    return cand


def _base_dir():
    """Diretório onde guardar o token.json: ao lado do .env (raiz do agent);
    se nenhum .env foi localizado, cai para a raiz da skill."""
    if _ENV_FILE:
        return os.path.dirname(os.path.abspath(_ENV_FILE))
    return os.path.abspath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir))


def _env(*names):
    """Retorna a primeira variável de ambiente definida e não vazia."""
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return None


class TokenStore:
    """Persiste os tokens em disco (token.json) com permissão 600.

    Resolve o problema de rotação: a Conta Azul troca o refresh_token a cada
    renovação, então o valor precisa ser regravado, senão a próxima renovação
    falha com invalid_grant. Também cacheia o access_token e seu vencimento para
    evitar renovar a cada chamada.

    Arquivo padrão: token.json ao lado do .env (raiz do agent). Já está no
    .gitignore. Mantém apenas tokens — nunca o client_secret.
    """

    def __init__(self, path=None):
        if path is None:
            path = os.path.join(_base_dir(), "token.json")
        self.path = path

    def load(self):
        # OSError cobre arquivo ausente e o caso de o caminho ser um diretório;
        # ValueError cobre JSON corrompido. Em qualquer um, começa vazio.
        try:
            with open(self.path) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}

    def save(self, refresh_token=None, access_token=None, expires_in=None):
        data = self.load()
        if refresh_token:
            data["refresh_token"] = refresh_token
        if access_token:
            data["access_token"] = access_token
        if expires_in:
            # margem de 60s para não usar um token quase expirado
            data["access_expires_at"] = int(time.time()) + int(expires_in) - 60
        # escreve num temporário (0600) e troca atomicamente — um crash no meio
        # da escrita não corrompe o token.json (que forçaria novo login).
        tmp = self.path + ".tmp"
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        os.replace(tmp, self.path)
        return data

    def valid_access_token(self):
        data = self.load()
        tok = data.get("access_token")
        exp = data.get("access_expires_at", 0)
        return tok if tok and time.time() < exp else None


class ContaAzulError(Exception):
    def __init__(self, status, body):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


class ContaAzulClient:
    def __init__(self, client_id, client_secret, refresh_token=None,
                 access_token=None, redirect_uri=None, store=None):
        if not client_id or not client_secret:
            raise ValueError("client_id e client_secret são obrigatórios")
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.redirect_uri = redirect_uri
        self.store = store

    @classmethod
    def from_env(cls, dotenv=True, store=True):
        if dotenv:
            load_dotenv()
        token_store = TokenStore() if store else None
        # tokens vêm preferencialmente do store (refletem a última rotação);
        # se o store ainda não existe, cai para o .env/ambiente como semente.
        saved = token_store.load() if token_store else {}
        return cls(
            client_id=_env("CONTA_AZUL_CLIENT_ID", "CLIENT_ID"),
            client_secret=_env("CONTA_AZUL_CLIENT_SECRET", "CLIENT_SECRET"),
            refresh_token=saved.get("refresh_token")
            or _env("CONTA_AZUL_REFRESH_TOKEN", "REFRESH_TOKEN"),
            access_token=token_store.valid_access_token() if token_store else
            _env("CONTA_AZUL_ACCESS_TOKEN", "ACCESS_TOKEN"),
            redirect_uri=_env("CONTA_AZUL_REDIRECT_URI", "REDIRECT_URI"),
            store=token_store,
        )

    def authorize_url(self, redirect_uri=None, state=None):
        """Etapa 1: monta a URL de login para o usuário autorizar no navegador."""
        redirect_uri = redirect_uri or self.redirect_uri
        if not redirect_uri:
            raise ValueError("redirect_uri é obrigatório para a URL de autorização")
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state or base64.urlsafe_b64encode(os.urandom(12)).decode(),
            "scope": SCOPE,
        }
        return LOGIN_URL + "?" + urllib.parse.urlencode(params)

    # --- OAuth -----------------------------------------------------------
    def _basic_header(self):
        raw = f"{self.client_id}:{self.client_secret}".encode()
        return "Basic " + base64.b64encode(raw).decode()

    def _token_request(self, data):
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(TOKEN_URL, data=body, method="POST")
        req.add_header("Authorization", self._basic_header())
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise ContaAzulError(e.code, e.read().decode()) from None
        self.access_token = payload.get("access_token", self.access_token)
        # IMPORTANTE: o refresh_token muda a cada renovação — persista-o.
        self.refresh_token = payload.get("refresh_token", self.refresh_token)
        if self.store:
            self.store.save(
                refresh_token=self.refresh_token,
                access_token=self.access_token,
                expires_in=payload.get("expires_in"),
            )
        return payload

    def exchange_code(self, code, redirect_uri=None):
        """Etapa 2: troca o authorization_code por tokens."""
        redirect_uri = redirect_uri or self.redirect_uri
        if not redirect_uri:
            raise ValueError("redirect_uri é obrigatório para a troca do code")
        return self._token_request({
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        })

    def refresh(self):
        """Etapa 3: renova o access_token usando o refresh_token."""
        if not self.refresh_token:
            raise ValueError("refresh_token ausente")
        return self._token_request({
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        })

    # --- API -------------------------------------------------------------
    def request(self, method, path, query=None, body=None, _retry=True):
        if not self.access_token:
            self.refresh()
        url = API_BASE + path
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method.upper())
        req.add_header("Authorization", f"Bearer {self.access_token}")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                ctype = resp.headers.get("Content-Type", "")
                if not raw:
                    return None
                # conteúdo não-JSON (ex.: PDF de venda) é devolvido como bytes
                if "application/json" in ctype or raw[:1] in (b"{", b"["):
                    return json.loads(raw.decode())
                return raw
        except urllib.error.HTTPError as e:
            if e.code == 401 and _retry and self.refresh_token:
                self.refresh()
                return self.request(method, path, query, body, _retry=False)
            raise ContaAzulError(e.code, e.read().decode()) from None

    def get(self, path, query=None):
        return self.request("GET", path, query=query)

    def post(self, path, body, query=None):
        return self.request("POST", path, query=query, body=body)

    def put(self, path, body, query=None):
        return self.request("PUT", path, query=query, body=body)

    def patch(self, path, body, query=None):
        return self.request("PATCH", path, query=query, body=body)

    def delete(self, path, query=None, body=None):
        # alguns endpoints (ex.: exclusão em lote) exigem corpo no DELETE
        return self.request("DELETE", path, query=query, body=body)


def _parse_query(items):
    # chaves repetidas viram lista (ex.: status=A status=B -> status=[A,B]),
    # que urlencode(doseq=True) serializa como parâmetros repetidos.
    q = {}
    for it in items or []:
        if "=" not in it:
            raise SystemExit(f"--query inválido: {it} (use chave=valor)")
        k, v = it.split("=", 1)
        if k in q:
            q[k] = q[k] + [v] if isinstance(q[k], list) else [q[k], v]
        else:
            q[k] = v
    return q


def main(argv=None):
    p = argparse.ArgumentParser(description="Cliente CLI da API Conta Azul")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("authorize-url", help="gerar a URL de login (etapa 1)")
    pa.add_argument("--redirect-uri")
    pa.add_argument("--state")

    pe = sub.add_parser("exchange", help="trocar code por tokens")
    pe.add_argument("--code", required=True)
    pe.add_argument("--redirect-uri")

    sub.add_parser("refresh", help="renovar access_token")

    for name in ("get", "post", "put", "patch", "delete"):
        sp = sub.add_parser(name, help=f"{name.upper()} em um caminho da API")
        sp.add_argument("path")
        sp.add_argument("--query", nargs="*", help="pares chave=valor")
        if name in ("post", "put", "patch"):
            sp.add_argument("--body", required=True, help="JSON do corpo")
        if name == "delete":
            sp.add_argument("--body", help="JSON do corpo (ex.: exclusão em lote)")

    args = p.parse_args(argv)
    cli = ContaAzulClient.from_env()

    if args.cmd == "authorize-url":
        print(cli.authorize_url(args.redirect_uri, args.state))
        return
    if args.cmd == "exchange":
        out = cli.exchange_code(args.code, args.redirect_uri)
    elif args.cmd == "refresh":
        out = cli.refresh()
    else:
        query = _parse_query(getattr(args, "query", None))
        if args.cmd == "get":
            out = cli.get(args.path, query=query)
        elif args.cmd == "delete":
            body = json.loads(args.body) if getattr(args, "body", None) else None
            out = cli.delete(args.path, query=query, body=body)
        else:
            body = json.loads(args.body)
            fn = {"post": cli.post, "put": cli.put, "patch": cli.patch}[args.cmd]
            out = fn(args.path, body=body, query=query)

    if args.cmd in ("exchange", "refresh"):
        # não imprime os tokens em claro — eles já foram salvos no token.json
        def _mask(t):
            return f"{t[:6]}...{t[-4:]} ({len(t)} chars)" if t else "—"
        print(json.dumps({
            "ok": True,
            "access_token": _mask(out.get("access_token")),
            "refresh_token": _mask(out.get("refresh_token")),
            "expires_in": out.get("expires_in"),
            "token_type": out.get("token_type"),
            "salvo_em": cli.store.path if cli.store else None,
        }, ensure_ascii=False, indent=2))
    elif isinstance(out, bytes):
        # resposta binária (ex.: PDF) — escreve crua no stdout para redirecionar
        sys.stdout.buffer.write(out)
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ContaAzulError, ValueError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
