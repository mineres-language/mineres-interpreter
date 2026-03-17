# mineres-lexer
Analisador léxico da linguagem de programação Minerês: tokeniza o código-fonte como primeira etapa do compilador.

---

## O que é um Analisador Léxico?

Um compilador funciona em etapas. A **análise léxica** é a primeira delas.

Ela recebe o código-fonte como uma sequência bruta de caracteres e o transforma em uma lista de **tokens**: unidades com significado dentro da linguagem.

**Exemplo:** o trecho abaixo em Minerês:

```
trem_di_numeru paozinhos fica_assim_entao 5 uai
```

é lido pelo lexer e transformado na seguinte lista de tokens:

```
("trem_di_numeru",  100, 1, 1)
("paozinhos",       300, 1, 16)
("fica_assim_entao",400, 1, 26)
("5",               200, 1, 43)
("uai",             502, 1, 45)
```

Cada token é uma tupla com quatro campos:

| Campo    | Descrição                                           |
|----------|-----------------------------------------------------|
| `lexema` | O texto original encontrado no código-fonte         |
| `código` | Um número que identifica a categoria do token       |
| `linha`  | A linha do código onde o token foi encontrado       |
| `coluna` | A coluna do código onde o token começa              |

---

## O que é um Token?

Um token representa a menor unidade com significado em um programa. Cada token pertence a uma **categoria**, identificada por um código numérico.

As categorias definidas para o Minerês são:

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
| `cabô`   | 501    | Fecha bloco             | `}`              |
| `uai`    | 502    | Fim de instrução        | `;`              |
| `(`      | 503    | Abre parêntese          | `(`              |
| `)`      | 504    | Fecha parêntese         | `)`              |
| `,`      | 505    | Separador de argumentos | `,`              |

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

## Estrutura do Repositório

```
mineres-lexer/
├── README.md               ← este arquivo
├── src/
│   ├── main.uai            ← entrada principal, orquestra a execução
│   ├── lexer.uai           ← lógica do analisador léxico
│   └── tokens.uai          ← definição dos códigos de cada token
├── tests/
│   ├── entrada.uai         ← arquivo de teste com código Minerês
│   └── saida_esperada.txt  ← saída esperada para validação
└── output/
    └── (arquivos .c gerados pela extensão ficam aqui)
```

### Descrição dos arquivos

**`tokens.uai`**: define todas as constantes numéricas que identificam cada tipo de token. É a base usada pelos outros arquivos.

**`lexer.uai`**: contém as funções que leem o código-fonte caractere por caractere, reconhecem os padrões e produzem a lista de tokens.

**`main.uai`**: ponto de entrada do programa. Abre o arquivo de código-fonte, chama o lexer e imprime a tabela de tokens resultante.

---

## Como executar

> O código é escrito em Minerês (`.uai`). A extensão [Minerês para VS Code](https://marketplace.visualstudio.com/items?itemName=grupo-mineres.mineres) transpila os arquivos `.uai` para C, que então é compilado normalmente.

1. Abra o projeto no VS Code com a extensão Minerês instalada
2. A extensão transpila os arquivos `.uai` para `.c` na pasta `output/`
3. Compile o `.c` gerado:
   ```bash
   gcc output/main.c -o lexer
   ```
4. Execute passando um arquivo Minerês como entrada:
   ```bash
   ./lexer tests/entrada.uai
   ```

---

## Equipe

| Nome | GitHub |
|------|--------|
| Celso Vinícius Sudário Fernandes | [@celzin](https://github.com/celzin) |
| Maria Eduarda Teixeira Souza | [@dudatsouza](https://github.com/dudatsouza) |
| Pedro Henrique Pires Dias | [@peudias](https://github.com/peudias) |

---

## Disciplina

Compiladores - Engenharia de Computação  
Primeira etapa: Análise Léxica