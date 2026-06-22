# Módulo: Gerador de Código Intermediário (IR)

O **Gerador de Código Intermediário** é a terceira etapa do interpretador. Ele recebe a sequência de tokens já validada pelo **[Analisador Sintático](./parser.md)** e transforma cada construção da linguagem Minerês em uma lista de **tuplas de baixo nível**, que representam o programa em uma forma independente de máquina, pronta para execução ou otimização futura.

---

## Detalhes da Implementação

A geração de IR foi integrada diretamente ao Parser de Descida Recursiva, eliminando a necessidade de uma Árvore Sintática Abstrata (AST) intermediária. Cada função do parser retorna a lista de tuplas correspondente à construção que analisou.

### Funcionalidades Principais:
* **Geração de Temporárias:** Resultados intermediários de expressões são armazenados em variáveis nomeadas `@_t1`, `@_t2`, `@_t3`, ... O prefixo `@_` garante que nunca conflitem com variáveis do usuário.
* **Geração de Labels:** Pontos de salto para controle de fluxo são nomeados `L1`, `L2`, `L3`, ...
* **Convenção `@` para variáveis:** Todas as variáveis de usuário no IR levam o prefixo `@` (ex: variável `x` → `@x`). Isso as distingue de literais e operações no arquivo de saída.
* **Análise Semântica:** Declaração e uso de variáveis são verificados durante a geração, detectando variáveis não declaradas e redeclarações. Tipos são rastreados e validados em cada operação.
* **Gestão de Erros:** Erros semânticos reportam a linha e coluna exatas e abortam a execução imediatamente.

---

## Novos Módulos (`src/ir/`)

| Arquivo              | Classe / Função    | Finalidade                                                           |
|----------------------|--------------------|----------------------------------------------------------------------|
| `geradores.py`       | `GeradorTemp`      | Gera nomes únicos para variáveis temporárias (`t1`, `t2`, ...)       |
| `geradores.py`       | `GeradorLabel`     | Gera nomes únicos para labels de salto (`L1`, `L2`, ...)             |
| `tabela_simbolos.py` | `TabelaSimbolos`   | Registra variáveis declaradas, seus tipos e posição no código-fonte  |
| `formatador.py`      | `formata_codigo()` | Converte a lista de tuplas Python no texto de saída do `saida_ir.uai`|

---

## Formato das Tuplas

Toda instrução do programa é representada por uma tupla de quatro elementos `(op, a, b, c)`. Valores ausentes são representados como `null` no arquivo de saída.

### Atribuição
```
("att", var, valor, null)
```

### Operações Aritméticas
```
("add",  res, op1, op2)    // +
("sub",  res, op1, op2)    // -
("mult", res, op1, op2)    // veiz
("div",  res, op1, op2)    // sob (real)
("divI", res, op1, op2)    // /   (inteira)
("mod",  res, op1, op2)    // %
```

### Operadores Unários
```
("uno", "+", res, op)
("uno", "-", res, op)
```

### Operações Lógicas
```
("and", res, op1, op2)     // tamem
("or",  res, op1, op2)     // quarque_um
("xor", res, op1, op2)     // um_o_oto
("not", res, op,  null)    // vam_marca
```

### Operadores Relacionais
```
("less", res, op1, op2)    // <
("leq",  res, op1, op2)    // <=
("gret", res, op1, op2)    // >
("geq",  res, op1, op2)    // >=
("eq",   res, op1, op2)    // mema_coisa
("dif",  res, op1, op2)    // neh_nada
```

### Entrada / Saída
```
("call", "read",  var,  null)    // xove
("call", "print", var,  null)    // oia_proce_ve com variável
("call", "print", null, valor)   // oia_proce_ve com literal
```

### Controle de Fluxo
```
("jump",  label, null,       null)
("if",    cond,  label_true, label_false)
("label", nome,  null,       null)
```

### For (`roda_esse_trem`)
```
... código de inicialização ...
("label", L_cond,  null,   null)
... código da condição ...
("if",    t_cond,  L_corpo, L_fim)
("label", L_corpo, null,   null)
... corpo do for ...
("label", L_incr,  null,   null)    // toca_o_trem salta para cá
... código do incremento ...
("jump",  L_cond,  null,   null)
("label", L_fim,   null,   null)
```
> `toca_o_trem` salta para `L_incr` (não para `L_cond`), garantindo que o incremento sempre seja executado antes da próxima verificação.

### Switch (`dependenu`)

Cada caso vira uma sequência de teste e salto condicional:
```
("eq",    @_t1,      @var_switch, valor_caso)
("if",    @_t1,      L_corpo,     L_proximo)
("label", L_corpo,   null,        null)
... corpo do caso ...
("jump",  L_fim,     null,        null)
("label", L_proximo, null,        null)
... próximos casos ...
("label", L_fim,     null,        null)
```
`para_o_trem` dentro de `dependenu` salta para `L_fim`.

---

## Análise Semântica

### Implementada

| Verificação                                  | Comportamento                                                                        |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| Variável não declarada                       | Erro fatal com linha e coluna                                                        |
| Redeclaração de variável                     | Erro fatal apontando a declaração anterior                                           |
| Inicialização automática por tipo            | `int`→`0`, `float`→`0.0`, `string`→`""`, `bool`→`"eh"`, `char`→`"\\0"`             |
| Lado esquerdo de atribuição inválido         | Erro fatal se não for um identificador declarado                                     |
| Atribuição com tipos incompatíveis           | Erro fatal; única exceção: `int → float` (coerção segura permitida)                 |
| Operadores lógicos com não-booleanos         | Erro fatal (`tamem`, `quarque_um`, `um_o_oto` exigem `trem_discolhe`)               |
| Divisão inteira `/` ou `%` com não-inteiros  | Erro fatal (ambos os operandos precisam ser `trem_di_numeru`)                        |
| Operação aritmética entre tipos incompatíveis| Erro fatal (ex: `string + int`)                                                      |
| Comparação entre tipos incompatíveis         | Erro fatal (ex: `string < int`)                                                      |
| Coerção numérica automática                  | `int op float` → resultado é `trem_cum_virgula`                                      |
| Soma de dois chars                           | `'a' + 'b'` → resultado é `trem_discrita`                                           |
| `para_o_trem` / `toca_o_trem` fora de laço  | Erro semântico fatal                                                                 |

Exemplo de feedback do sistema:

```
[ERRO SEMÂNTICO]
Linha: 7, Coluna: 5
Variável 'x' usada sem ter sido declarada.
Execução abortada.
```

---

## Exemplo

**Entrada (`entrada.uai`):**
```
bora_cumpade main()
simbora
    trem_di_numeru a, b uai
    a fica_assim_entao 10 uai
    b fica_assim_entao a + 5 uai
    oia_proce_ve(b) uai
cabo
```

**Saída (`saida_ir.uai`):**
```
[
	("att", @a, 0, null),
	("att", @b, 0, null),
	("att", @a, 10, null),
	("add", @_t1, @a, 5),
	("att", @b, @_t1, null),
	("call", "print", @b, null)
]
```

> **Convenções de formatação:**
> - Operações (ex: `"att"`, `"add"`, `"print"`) são impressas com aspas duplas.
> - Variáveis de usuário (ex: `@a`) e temporárias (ex: `@_t1`) são impressas **sem aspas** — o prefixo `@` as identifica.
> - Labels (ex: `L1`) são impressos sem aspas.
> - Strings literais do código-fonte (ex: `"ola"`) mantêm suas aspas.
> - Inteiros, floats e `null` são impressos sem aspas.

---

[Voltar para a Documentação Principal](../README.md)
