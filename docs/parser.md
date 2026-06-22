# Módulo: Analisador Sintático (Parser)

O **Analisador Sintático** (Parser) é a segunda etapa fundamental do interpretador. Ele recebe a lista de tokens gerada pelo **[Analisador Léxico](../lexer/README.md)** e verifica se a sequência e a organização desses tokens respeitam as regras gramaticais da linguagem Minerês.

---

## Detalhes da Implementação

O Parser foi implementado utilizando a técnica de **Descida Recursiva** (*Recursive Descent*). Trata-se de um analisador *top-down* preditivo, onde cada regra da gramática é traduzida em uma função específica no código Python, permitindo uma validação estruturada e hierárquica.

### Funcionalidades Principais:
* **Análise Preditiva:** Utiliza o conceito de conjuntos **First** (símbolos iniciais) para decidir qual caminho de derivação seguir sem a necessidade de retrocesso (*backtracking*).
* **Validação de Escopo:** Garante que o código funcional esteja obrigatoriamente dentro da estrutura principal (`bora_cumpade main`).
* **Gestão de Erros Sintáticos:** Emite alertas detalhados quando um token inesperado é encontrado, reportando o que era esperado e o que foi recebido, com a localização exata de linha e coluna.
* **Análise Semântica de Tipos:** Durante o parsing, rastreia o tipo de cada expressão e valida as operações, emitindo erros semânticos para operações inválidas (ex: somar `string` com `int`, usar `and` com não-booleanos, divisão inteira com float).

---

## Estrutura Gramatical (EBNF)

A [gramática do Minerês](../../data/grammar/mineres.gmr) define como as "frases" da linguagem devem ser montadas. Abaixo, alguns exemplos das produções implementadas no código:

### 1. Ponto de Entrada
```ebnf
<function> ::= 'bora_cumpade' 'main' '(' ')' <bloco>
<bloco>    ::= 'simbora' <stmtList> 'cabo'
```

### 2. Comandos de Fluxo e Controle
```ebnf
<ifStmt>    ::= 'uai_se' '(' <expr> ')' <stmt> ['uai_senao' <stmt>]

<whileStmt> ::= 'enquanto_tiver_trem' '(' <expr> ')' <stmt>

<forStmt>   ::= 'roda_esse_trem' '(' [<atrib>] ';' [<atrib>] ';' [<atrib>] ')' <stmt>

<caseStmt>  ::= 'dependenu' '(' IDENT ')' 'simbora'
                    ('du_casu' <fatorZin> ':' <stmt>)*
                    ['uai_so' ':' <stmt>]
                'cabo'
```

### 3. Precedência de Operadores
Para garantir que a semântica matemática seja respeitada (ex: multiplicação antes da soma), o Parser implementa uma hierarquia de funções recursivas. A ordem de precedência (do menor para o maior) é:

| Nível       | Operadores                                     | Função Parser       |
|-------------|------------------------------------------------|---------------------|
| Atribuição  | `fica_assim_entao`                             | `parse_atrib`       |
| OR lógico   | `quarque_um`                                   | `parse_or`          |
| XOR lógico  | `um_o_oto`                                     | `parse_xor`         |
| AND lógico  | `tamem`                                        | `parse_and`         |
| NOT lógico  | `vam_marca`                                    | `parse_not`         |
| Relacionais | `mema_coisa`, `neh_nada`, `<`, `>`, `<=`, `>=` | `parse_rel`         |
| Aditivos    | `+`, `-`                                       | `parse_add`         |
| Multiplicat.| `veiz`, `sob`, `/`, `%`                        | `parse_mult`        |
| Unários     | `+`, `-`                                       | `parse_uno`         |
| Primários   | Identificadores, Literais, `( <expr> )`        | `parse_fatorZao`    |

### 4. Análise Semântica de Tipos

O Parser rastreia o tipo de cada sub-expressão e aplica regras estritamente:

| Regra                                       | Comportamento                                                                  |
|---------------------------------------------|--------------------------------------------------------------------------------|
| Operadores lógicos (`tamem`, `quarque_um`, `um_o_oto`) | Exigem dois `trem_discolhe`; erro caso contrário              |
| `vam_marca` (NOT)                           | Exige operando `trem_discolhe`                                                 |
| Operadores relacionais                      | Aceita dois numéricos (`int`/`float`) ou dois do mesmo tipo; erro caso contrário |
| Divisão inteira `/` e módulo `%`            | Exigem dois `trem_di_numeru`; erro se um for float                             |
| Soma de chars (`'a' + 'b'`)                 | Resultado do tipo `trem_discrita` (string concatenada)                         |
| Coerção numérica (`int` + `float`)          | Resultado promovido automaticamente para `trem_cum_virgula`                    |
| Atribuição com tipos incompatíveis          | Erro semântico, exceto `int → float` que é permitido                          |
| `para_o_trem` / `toca_o_trem` fora de laço | Erro semântico fatal                                                           |

Exemplo de feedback semântico:

```
[ERRO SEMÂNTICO]
Linha: 4, Coluna: 3
Operacao matematica invalida entre os tipos 'trem_discrita' e 'trem_di_numeru'.
```

### 5. Tratamento de Erros Sintáticos
O Parser é projetado para interromper a execução assim que uma estrutura inválida é detectada, evitando que erros se propaguem para as fases futuras do interpretador.

Exemplo de feedback do sistema:

```
[ERRO SINTÁTICO]
Linha: 5, Coluna: 12
Esperava: 'uai'
Recebi  : 'trem_di_numeru'
Execução abortada.
```

### 6. Principais Métodos

| Método                | Finalidade                                                                                |
|-----------------------|-------------------------------------------------------------------------------------------|
| `consome()`           | Valida o token atual e avança o cursor. Se o token for inválido, dispara o erro fatal.    |
| `parse_stmtList()`    | Processa recursivamente a lista de comandos dentro de um bloco.                           |
| `parse_declaration()` | Declara variáveis na tabela de símbolos e gera tuplas `att` de inicialização.             |
| `parse_atrib()`       | Gerencia a lógica de atribuição de valores a variáveis, com validação de tipos.           |
| `parse_ioStmt()`      | Lida com os comandos de entrada (`xove`) e saída (`oia_proce_ve`).                        |
| `parse_ifStmt()`      | Gera IR para condicional `uai_se` / `uai_senao`.                                          |
| `parse_whileStmt()`   | Gera IR para laço `enquanto_tiver_trem`.                                                  |
| `parse_forStmt()`     | Gera IR para laço `roda_esse_trem`, com label separado para o incremento (suporte a `toca_o_trem`). |
| `parse_caseStmt()`    | Gera IR para `dependenu`, transformando cada `du_casu` em teste de igualdade + salto.     |
| `_validar_operacao_matematica()` | Fiscaliza operações aritméticas e retorna o tipo do resultado.              |
| `_validar_operacao_logica()`     | Garante que operandos lógicos são booleanos.                                |
| `_validar_operacao_relacional()` | Verifica compatibilidade de tipos em comparações.                           |

---

[Voltar para a Documentação Principal](../../README.md)