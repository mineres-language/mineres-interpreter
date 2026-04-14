# Minerês Interpreter

Este repositório contém o desenvolvimento de um interpretador para a linguagem [**Minerês**](https://mineres-language.github.io/). O objetivo desse projeto é aplicar conceitos da disciplina de **Compiladores** para construir uma infraestrutura capaz de processar, validar e executar um dialeto customizado.

---

## Arquitetura do Interpretador

O software foi projetado seguindo um modelo de **pipeline modular**, onde cada fase da compilação é isolada em seu próprio submódulo, facilitando a manutenção e a expansão futura.

### Mapa de Documentação Técnica

Para entender os detalhes de implementação de cada componente, acesse as documentações específicas:

1.  **[Core: Analisador Léxico (Lexer)](./src/lexer/README.md)**
    * Responsável pela tokenização e reconhecimento de padrões via AFD.
2.  **[Core: Analisador Sintático (Parser)](./src/parser/README.md)**
    * Responsável pela validação gramatical e hierarquia de expressões.
3.  **[Infra: Recursos e Suíte de Testes (Data)](./data/)**
    * Gerenciamento da gramática formal (.gmr) e arquivos de entrada/saída (.uai).
4.  **[Próxima Fase: Em construção ]**
    * Em construção.

---

### Estrutura de Diretórios

```
mineres-interpreter/
├── data/
│   ├── grammar/
│   │   └── mineres.gmr       # Definição formal da gramática
│   ├── input/                # Arquivos de teste (.uai)
│   │   ├── entrada.uai
│   │   └── teste_1.uai...
│   └── output/               # Resultados do processamento
│       └── saida.uai
├── src/
│   ├── lexer/                # Analisador Léxico
│   │   ├── lexer.py
│   │   ├── tokens.py
│   │   └── README.md
│   ├── parser/               # Analisador Sintático
│   │   ├── parser.py
│   │   └── README.md
│   └── main.py               # Ponto de entrada da aplicação
├── .gitignore
└── README.md                 # Documentação principal
```

## Como Executar

> O interpretador foi desenvolvido inteiramente em Python. Para testá-lo em sua máquina, siga os passos abaixo:

### Pré-requisitos
* Python 3.10 ou superior.

### Instruções
1. Clone o repositório e abra a pasta do projeto `(mineres-interpreter)` no terminal.
2. Insira o código fonte Minerês no arquivo `data/input/entrada.uai`.
3. Execute o interpretador:
   ```bash
   python src/main.py
   ```
4. O resultado será impresso no terminal.

## Equipe

| Nome | GitHub |
|------|--------|
| Celso Vinícius Sudário Fernandes | [@celzin](https://github.com/celzin) |
| Maria Eduarda Teixeira Souza | [@dudatsouza](https://github.com/dudatsouza) |
| Pedro Henrique Pires Dias | [@peudias](https://github.com/peudias) |

---

## Disciplina

Compiladores - Engenharia de Computação  