# Módulo: Analisador Léxico (Lexer)

O **Analisador Léxico** é a porta de entrada do interpretador. Sua função é ler o fluxo bruto de caracteres do código-fonte em Minerês e transformá-lo em uma sequência de **Tokens** lógicos, servindo de base para a **[análise sintática](../parser/README.md)**

---

## Detalhes da Implementação

O motor do Lexer foi construído manualmente como um **Autômato Finito Determinístico (AFD)**. Diferente de geradores automáticos, a implementação manual permite um controle sobre o consumo de caracteres e a geração de mensagens de erro customizadas.

### Funcionalidades Principais:
* **Gestão de Erros:** O Lexer identifica falhas críticas e aborta a execução imediatamente, reportando a **linha** e **coluna** exatas.
* **Comentários:** * **Linha:** Identificados por `//`.
    * **Bloco:** Suporte a comentários multilinha com a sintaxe `causo ... fim_do_causo`.
* **Processamento de Escapes:** Reconhece e converte sequências de escape dentro de strings (ex: `\n`, `\t`, `\"`).

---

## O que é um Token?

Um token representa a menor unidade com significado para o interpretador. No Minerês, cada token é exportado como uma tupla contendo metadados essenciais para o rastreio de erros:

**Estrutura:** `(lexema, código, linha, coluna)`

### Exemplo de Processamento:
**Entrada:** `trem_di_numeru pão fica_assim_entao 5 uai`

**Saída de Tokens:**
```python
("trem_di_numeru",   100, 1, 1)
("pão",              300, 1, 16)
("fica_assim_entao", 400, 1, 20)
("5",               200, 1, 37)
("uai",              502, 1, 39)
```

### Categorias de Tokens

Os tokens são organizados por intervalos numéricos definitdos em [tokens.py](./tokens.py).

### Palavras Reservadas (códigos 100–199)

São as palavras que fazem parte da sintaxe da linguagem: não podem ser usadas como nomes de variáveis ou funções.

| Lexema              | Código | Equivalente em C       |
|---------------------|--------|------------------------|
| `trem_di_numeru`    | 100    | `int`                  |
| `trem_cum_virgula`  | 101    | `float`                |
| `trem_discrita`     | 102    | `char *` (string)      |
| `trem_discolhe`     | 103    | `bool`                 |
| `trosso`            | 104    | `char`                 |
| `uai_se`            | 110    | `if`                   |
| `uai_senao`         | 111    | `else`                 |
| `dependenu`         | 112    | `switch`               |
| `du_casu`           | 113    | `case`                 |
| `roda_esse_trem`    | 120    | `for`                  |
| `enquanto_tiver_trem` | 121  | `while`                |
| `para_o_trem`       | 122    | `break`                |
| `toca_o_trem`       | 123    | `continue`             |
| `bora_cumpade`      | 130    | `function` / `main`    |
| `ta_bao`            | 131    | `return`               |
| `oia_proce_ve`      | 140    | `printf`               |
| `xove`              | 141    | `scanf`                |

> O intervalo 100–199 é reservado para palavras-chave. Nem todos os números do intervalo precisam ser usados. Os espaços vazios existem para facilitar futuras adições à linguagem.

### Literais (códigos 200–299)

São valores concretos escritos diretamente no código.

| Tipo             | Código | Exemplo         | Expressão Regular                            |
|------------------|--------|-----------------|----------------------------------------------|
| Número inteiro   | 200    | `0`, `42`       | `0⁺ ∪ [1-9][0-9]*`                          |
| Número hexadecimal | 201  | `0x3AF8`        | `0x([0-9] ∪ [A-F])⁺`                        |
| Número octal     | 202    | `017`           | `0[1-7][0-7]*`                               |
| Número float     | 203    | `3.14`, `.92`   | `[0-9]+.[0-9]* ∪ [0-9]*.[0-9]+`             |
| String           | 204    | `"Uai, sô!"`    | `" Σ* "`                                     |
| Char (trosso)    | 205    | `.'A'.`         | `.'` + qualquer caractere + `'.`             |

### Identificadores (código 300)

São os nomes criados pelo programador para variáveis e funções.

| Tipo          | Código | Exemplo       | Expressão Regular                          |
|---------------|--------|---------------|--------------------------------------------|
| Identificador | 300    | `paozinhos`   | `[a-zA-Z][a-zA-Z0-9_]*`                   |

> Um identificador deve começar com uma letra e pode conter letras, dígitos e underline `_`. Não pode começar com número.

### Operadores (códigos 400–499)

São os símbolos e palavras usados para realizar operações.

| Lexema             | Código | Tipo           | Equivalente em C |
|--------------------|--------|----------------|------------------|
| `fica_assim_entao` | 400    | Atribuição     | `=`              |
| `mema_coisa`       | 401    | Igualdade      | `==`             |
| `neh_nada`         | 402    | Diferente      | `!=`             |
| `<`                | 403    | Menor          | `<`              |
| `>`                | 404    | Maior          | `>`              |
| `<=`               | 405    | Menor ou igual | `<=`             |
| `>=`               | 406    | Maior ou igual | `>=`             |
| `+`                | 410    | Adição         | `+`              |
| `-`                | 411    | Subtração      | `-`              |
| `veiz`             | 412    | Multiplicação  | `*`              |
| `sob`              | 413    | Divisão        | `/`              |
| `%`                | 414    | Módulo         | `%`              |
| `tamem`            | 420    | E lógico       | `&&`             |
| `quarque_um`       | 421    | OU lógico      | `\|\|`           |
| `vam_marca`        | 422    | NÃO lógico     | `!`              |
| `um_o_oto`         | 423    | XOR lógico     | `^`              |

### Delimitadores (códigos 500–599)

São os símbolos que estruturam o código. Abrem e fecham blocos, separam argumentos, encerram instruções.

| Lexema   | Código | Função                  | Equivalente em C |
|----------|--------|-------------------------|------------------|
| `simbora`| 500    | Abre bloco              | `{`              |
| `cabo`   | 501    | Fecha bloco             | `}`              |
| `uai`    | 502    | Fim de instrução        | `;`              |
| `(`      | 503    | Abre parêntese          | `(`              |
| `)`      | 504    | Fecha parêntese         | `)`              |
| `,`      | 505    | Separador de argumentos | `,`              |
| `{`      | 506    | Abre chave (símbolo)    | `{`              |
| `}`      | 507    | Fecha chave (símbolo)   | `}`              |
| `.`      | 508    | Ponto Final             | `.`              |

### Erros Léxicos (códigos 900–999)

Quando o lexer encontra algo que não reconhece ou que está malformado, ele registra um **erro léxico**, mas continua tentando processar o restante do código.

| Tipo de Erro                    | Código | Exemplo                        |
|---------------------------------|--------|--------------------------------|
| String não fechada              | 900    | `"Uai, sô!` (sem fechar `"`)  |
| Número mal formado              | 901    | `0x3GZ` (hex inválido)         |
| Símbolo desconhecido            | 902    | `@`, `#`, `$`                  |
| Comentário multilinha não fechado | 903  | `causo` sem `fim do causo`     |

---

## Nomenclatura das Constantes

Cada constante de código segue o padrão `PREFIXO_NOME`, onde o prefixo indica a categoria:

| Prefixo | Categoria           | Exemplo               |
|---------|---------------------|-----------------------|
| `PR_`   | Palavra Reservada   | `PR_UAI_SE`           |
| `LIT_`  | Literal             | `LIT_NUM_INT`         |
| `OP_`   | Operador            | `OP_FICA_ASSIM_ENTAO` |
| `DEL_`  | Delimitador         | `DEL_SIMBORA`         |
| `ERRO_` | Erro Léxico         | `ERRO_STRING`         |

Identificadores não têm prefixo composto. Nesse código é simplesmente `IDENTIFICADOR` (300).

Essa convenção permite verificações rápidas no lexer usando os intervalos numéricos. Por exemplo, para saber se um token é uma palavra reservada:

```
uai_se (codigo >= 100 tamem codigo <= 199)
simbora
    oia_proce_ve "É uma palavra reservada!" uai
cabô
```

---

## Expressões Regulares

O lexer usa expressões regulares para reconhecer cada categoria de token. Elas definem os padrões válidos de caracteres:

| Símbolo | Significado                          |
|---------|--------------------------------------|
| `*`     | Zero ou mais repetições              |
| `+`     | Uma ou mais repetições               |
| `∪`     | União (ou)                           |
| `[a-z]` | Qualquer caractere entre a e z       |
| `Σ`     | Qualquer caractere do alfabeto       |

---

[Voltar para a Documentação Principal](../../README.md)