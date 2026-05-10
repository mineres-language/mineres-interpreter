# Módulo: Analisador Sintático (Parser)

O **Analisador Sintático** (Parser) é a segunda etapa fundamental do interpretador. Ele recebe a lista de tokens gerada pelo **[Analisador Léxico](../lexer/README.md)** e verifica se a sequência e a organização desses tokens respeitam as regras gramaticais da linguagem Minerês.

---

## Detalhes da Implementação

O Parser foi implementado utilizando a técnica de **Descida Recursiva** (*Recursive Descent*). Trata-se de um analisador *top-down* preditivo, onde cada regra da gramática é traduzida em uma função específica no código Python, permitindo uma validação estruturada e hierárquica.

### Funcionalidades Principais:
* **Análise Preditiva:** Utiliza o conceito de conjuntos **First** (símbolos iniciais) para decidir qual caminho de derivação seguir sem a necessidade de retrocesso (*backtracking*).
* **Validação de Escopo:** Garante que o código funcional esteja obrigatoriamente dentro da estrutura principal (`bora_cumpade main`).
* **Gestão de Erros Sintáticos:** Emite alertas detalhados quando um token inesperado é encontrado, reportando o que era esperado e o que foi recebido, com a localização exata de linha e coluna.

---

## Estrutura Gramatical (EBNF)

A [gramática do Minerês](../../data/grammar/mineres.gmr) define como as "frases" da linguagem devem ser montadas. Abaixo, alguns exemplos das produções implementadas no código:

### 1. Ponto de Entrada
```ebnf
<function> ::= 'bora_cumpade' 'main' '(' ')' <bloco>
<bloco>    ::= 'simbora' <stmtList> 'cabo'
```

### 2. Comandos de Fluxo e Controle
Condicional: uai_se (condicao) <stmt> [uai_senao <stmt>]

Repetição Enquanto: enquanto_tiver_trem (condicao) <stmt>

Repetição Para: roda_esse_trem (atrib; cond; atrib) <stmt>

Seleção: dependenu (ident) simbora { du_casu valor: <stmt> } [uai_so: <stmt>] cabo

# 3. Precedência de Operadores
Para garantir que a semântica matemática seja respeitada (ex: multiplicação antes da soma), o Parser implementa uma hierarquia de funções recursivas. A ordem de precedência (do menor para o maior) é:

**Atribuição:** fica_assim_entao

**Lógicos (OR, XOR, AND):** quarque_um, um_o_oto, tamem

**Relacionais:** mema_coisa, neh_nada, <, >, <=, >=

**Aditivos:** +, -

**Multiplicativos:** veiz, sob, /, %

**Unários:** +, -, vam_marca (NOT)

**Primários:** Identificadores, Literais e subexpressões entre parênteses ( )

### 4. Tratamento de Erros Sintáticos
O Parser é projetado para interromper a execução assim que uma estrutura inválida é detectada, evitando que erros se propaguem para as fases futuras do interpretador.

Exemplo de feedback do sistema:

```
[ERRO SINTÁTICO]
Linha: 5, Coluna: 12
Esperava: 'uai'
Recebi  : 'trem_di_numeru'
Execução abortada.
```

### 5. Principais Métodos

| Método                | Finalidade                                                                                |
|-----------------------|-------------------------------------------------------------------------------------------|
| `consome()`           | Valida o token atual e avança o cursor. Se o token for inválido, dispara o erro fatal.    |
| `parse_stmtList()`    | Processa recursivamente a lista de comandos dentro de um bloco.                           |
| `parse_atrib()`       | Gerencia a lógica de atribuição de valores a variáveis.                                   |
| `parse_ioStmt`        | Lida com os comandos de entrada (xove) e saída (oia_proce_ve).                            |

---

[Voltar para a Documentação Principal](../../README.md)