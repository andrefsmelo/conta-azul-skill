# API de Produtos (Estoque) — v1

API da Conta Azul (`open-api-inventory`), **mesmo host e mesma autenticação** do
Financeiro: `https://api-v2.contaazul.com`, header `Authorization: Bearer
<token>`. O `scripts/ca_client.py` chama estes endpoints sem alteração.

Gerencia o **catálogo de produtos** (cadastro, estoque, fiscal, e-commerce,
kits e variações) e tabelas auxiliares (NCM, CEST, unidades de medida, etc.).
É a origem dos IDs de item usados em vendas e contratos.

Convenções: `tamanho_pagina` aceita `10, 20, 50, 100, 200, 500, 1000`; datas em
ISO-8601. **(obrig.)** = obrigatório.

> ⚠️ **Envelope de resposta inconsistente** (verificado em chamada real): a
> listagem `GET /v1/produtos` retorna `{ "totalItems": N, "items": [...] }`,
> mas os lookups (ex.: `unidades-medida`) retornam `{ "total_items": N,
> "items": [...] }`. Compare com o Financeiro (`itens_totais`/`itens`). Não
> assuma o nome do campo de total — confira por endpoint.

---

## Endpoints

### `GET /v1/produtos` — listar/filtrar
Sem parâmetros obrigatórios. Filtros (query):
| Param | Tipo | Notas |
| --- | --- | --- |
| `pagina` / `tamanho_pagina` | integer | paginação |
| `busca` | string | busca textual |
| `status` | string | `ATIVO` \| `INATIVO` |
| `sku` | string | filtra por SKU |
| `valor_venda_inicial` / `valor_venda_final` | number | faixa de preço |
| `integracao_ecommerce_ativo` | boolean | |
| `produtos_kit_ativo` | boolean | |
| `data_alteracao_de` / `_ate` | string | ISO |
| `campo_ordenacao` | string | `NOME` \| `CODIGO` \| `VALOR_VENDA` |
| `direcao_ordenacao` | string | `ASC` \| `DESC` |

### `POST /v1/produtos` — criar
Body: `CriacaoProduto` (abaixo).

### `GET /v1/produtos/{id}` — detalhar
Path: `id` **(obrig.)**.

### `PATCH /v1/produtos/{id}` — atualizar (parcial)
Path: `id` **(obrig.)**. Body: `AtualizacaoParcialProduto` (campos a alterar).

### `DELETE /v1/produtos/{id}` — remover
Path: `id` **(obrig.)**.

### Tabelas auxiliares (lookup) — todas `GET`, com `busca_textual` e paginação
| Endpoint | Conteúdo |
| --- | --- |
| `GET /v1/produtos/categorias` | grupos/categorias de produto |
| `GET /v1/produtos/unidades-medida` | unidades de medida (id usado no produto) |
| `GET /v1/produtos/ncm` | códigos NCM |
| `GET /v1/produtos/cest` | códigos CEST |
| `GET /v1/produtos/ecommerce-categorias` | categorias de e-commerce |
| `GET /v1/produtos/ecommerce-marcas` | marcas de e-commerce |

---

## Schema: CriacaoProduto

Apenas `nome` é obrigatório no topo; o resto é opcional e organizado em blocos.

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `nome`* | string | Nome do produto |
| `descricao` | string | Descrição |
| `codigo_sku` / `codigo_ean` | string | SKU / EAN |
| `ativo` | boolean | |
| `status` | enum | `ATIVO` \| `INATIVO` |
| `formato` | enum | `SIMPLES` \| `VARIACAO` |
| `categoria` | objeto | `{ "id": <int> }` — grupo (de `GET .../categorias`) |
| `unidade_medida` | objeto | `{ "id": <int> }` (de `GET .../unidades-medida`) |
| `id_centro_custo` | string | Centro de custo |
| `estoque` | objeto | `valor_venda`, `custo_medio`, `estoque_disponivel/minimo/maximo` |
| `fiscal` | objeto | `origem`, `tipo_produto`, `ncm`, `cest`, `unidade_medida` |
| `pesos_dimensoes` | objeto | `peso_bruto/liquido`, `altura`, `largura`, `profundidade`, `volumes` |
| `ecommerce` | objeto | SEO, marca, categoria, `condicao`, `integracao_ativa` |
| `detalhe_kit` | objeto | `itens[]`, `valor_venda` (quando é kit) |
| `variacao` | objeto | `tipos[]`, `produtos[]` (quando `formato = VARIACAO`) |
| `conversoes_unidade_medida` | array | conversões entre unidades |

### Exemplo mínimo
```json
{
  "nome": "Produto Teste",
  "codigo_sku": "SKU-001",
  "estoque": { "valor_venda": 99.90, "estoque_disponivel": 10 }
}
```

---

## Enums principais

- **FormatoDoProduto**: `SIMPLES`, `VARIACAO`.
- **StatusDoProduto**: `ATIVO`, `INATIVO`.
- **CondicaoDoProdutoNoEcommerce**: `NOVO`, `USADO`.
- **TipoDoProduto**: `MERCADORIA_PARA_REVENDA`, `MATERIA_PRIMA`, `EMBALAGEM`,
  `PRODUTO_EM_PROCESSO`, `PRODUTO_ACABADO`, `SUBPRODUTO`,
  `PRODUTO_INTERMEDIARIO`, `MATERIAL_DE_USO_E_CONSUMO`, `ATIVO_IMOBILIZADO`,
  `SERVICOS`, `OUTROS_INSUMOS`, `OUTRAS`.
- **OrigemDoProduto**: `NACIONAL`, `ESTRANGEIRA_IMPORTACAO_DIRETA`,
  `ESTRANGEIRA_ADQUIRIDA_INTERNAMENTE`, `NACIONAL_IMPORTACAO_SUPERIOR_40`,
  `NACIONAL_PRODUCAO_CONFORMIDADE`, `NACIONAL_IMPORTACAO_INFERIOR_40`,
  `ESTRANGEIRA_IMPORTACAO_DIRETA_CAMEX`,
  `ESTRANGEIRA_ADQUIRIDA_INTERNAMENTE_CAMEX`,
  `NACIONAL_MERCDORIA_BEM_IMPORTACAO_SUPERIOR_70`.

> Fonte: <https://developers.contaazul.com/open-api-docs/open-api-inventory/v1>
