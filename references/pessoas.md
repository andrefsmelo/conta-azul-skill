# API de Pessoas — v1

API da Conta Azul (`open-api-person`), **mesmo host e mesma autenticação** do
Financeiro: `https://api-v2.contaazul.com`, header `Authorization: Bearer
<token>`. O `scripts/ca_client.py` chama estes endpoints sem alteração.

Gerencia **clientes, fornecedores e transportadoras** (pessoas físicas,
jurídicas ou estrangeiras). É a origem dos IDs de `contato`/`cliente` usados em
eventos financeiros e contratos.

Convenções: `tamanho_pagina` aceita `10, 20, 50, 100, 200, 500, 1000`; datas em
ISO-8601. **(obrig.)** = obrigatório.

> ⚠️ **Envelope de resposta diferente do Financeiro.** A listagem retorna
> `{ "totalItems": N, "items": [...] }` (inglês/camelCase), enquanto o Financeiro
> usa `{ "itens_totais": N, "itens": [...] }`. Verificado em chamada real.
> Cada pessoa traz `id`, `nome`, `perfis`, `tipo_pessoa`, `id_legado`,
> `uuid_legado`, `ativo`, etc.

---

## Endpoints

### `GET /v1/pessoas` — listar/filtrar
Sem parâmetros obrigatórios. Principais filtros (todos query):
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` / `tamanho_pagina` | integer | paginação |
| `busca` | string | busca textual |
| `tipos_pessoa` | string | `Física` \| `Jurídica` \| `Estrangeira` |
| `tipo_perfil` | string | `Cliente` \| `Fornecedor` \| `Transportadora` |
| `ids` / `documentos` / `emails` / `nomes` / `telefones` | string | filtros diretos |
| `codigos_pessoa` / `cidades` / `ufs` / `paises` | string | |
| `data_criacao_inicio` / `_fim` | string | ISO |
| `data_alteracao_de` / `_ate` | string | ISO |
| `com_endereco` | boolean | inclui endereços na resposta |
| `tipo_ordenacao` | string | `NOME` \| `EMAIL` \| `DOCUMENTO` \| `ATIVO` |
| `ordem_ordenacao` | string | `ASC` \| `DESC` |

### `POST /v1/pessoas` — criar
Body: `CriarPessoa` (abaixo).

### `GET /v1/pessoas/{id}` — detalhar
Path: `id` **(obrig.)**.

### `GET /v1/pessoas/legado/{id}` — detalhar por ID legado
Path: `id` **(obrig.)** — o ID da API antiga.

### `PUT /v1/pessoas/{id}` — atualizar (completo)
Path: `id` **(obrig.)**. Body: `AtualizarPessoa` (mesma forma do `CriarPessoa`).

### `PATCH /v1/pessoas/{id}` — atualizar (parcial)
Path: `id` **(obrig.)**. Body: `AtualizacaoParcialPessoa` (campos a alterar).

### `GET /v1/pessoas/conta-conectada` — empresa do token
Sem parâmetros. Retorna os dados cadastrais da empresa vinculada ao token
(razão social, CNPJ, etc.). Útil para validar qual empresa está conectada.

### `POST /v1/pessoas/ativar` · `POST /v1/pessoas/inativar` — status em lote
Body: `{ "uuids": ["id1", "id2", ...] }` — **máximo 10 IDs** por chamada.

### `POST /v1/pessoas/excluir` — excluir em lote
Body: `{ "uuids": ["id1", ...] }`.

---

## Schema: CriarPessoa (e AtualizarPessoa)

Campos com `*` são obrigatórios.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `nome`* | string | Nome da pessoa |
| `tipo_pessoa`* | enum | `Física` \| `Jurídica` \| `Estrangeira` |
| `cpf` | string | CPF (pessoa física) |
| `cnpj` | string | CNPJ (pessoa jurídica) |
| `nome_fantasia` | string | Nome fantasia (PJ) |
| `email` | string | Emails separados por vírgula |
| `telefone_celular` / `telefone_comercial` | string | |
| `rg` / `data_nascimento` | string | Pessoa física |
| `codigo` | string | Código da pessoa |
| `ativo` | boolean | |
| `optante_simples` | boolean | Optante do Simples Nacional |
| `observacao` | string | |
| `perfis` | array | `[{ "tipo_perfil": "Cliente" }]` — ver `Perfil` |
| `enderecos` | array | ver Endereço |
| `inscricoes` | array | inscrição estadual/municipal/SUFRAMA |
| `outros_contatos` | array | contatos adicionais |
| `contato_cobranca_faturamento` | objeto | `{ emails[], whatsapp }` |

### Endereço (item de `enderecos`)
`logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `estado`, `cep`,
`pais` (todos string).

### Perfil (item de `perfis`)
| Campo | Tipo | Descrição |
| --- | --- | --- |
| `tipo_perfil`* | enum | `Cliente` \| `Fornecedor` \| `Transportadora` |

### Exemplo mínimo (cliente PJ)
```json
{
  "nome": "ACME Ltda",
  "tipo_pessoa": "Jurídica",
  "cnpj": "12345678000190",
  "email": "contato@acme.com",
  "perfis": [{ "tipo_perfil": "Cliente" }]
}
```

---

## Enums

- **TipoPessoa**: `Física`, `Jurídica`, `Estrangeira`.
- **Perfil**: `Cliente`, `Fornecedor`, `Transportadora`.
- **Indicador** (inscrição estadual): `NAO CONTRIBUINTE`, `CONTRIBUINTE`,
  `ISENTO`.

> Fonte: <https://developers.contaazul.com/open-api-docs/open-api-person/v1>
