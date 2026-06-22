# Módulo: Dados e Recursos (Data)

Este diretório centraliza o suporte do interpretador **Minerês**, separando a definição formal da linguagem e os conjuntos de testes da lógica de processamento presente no diretório `src/`.

---

## Estrutura de Conteúdo

### 1. [/grammar](https://github.com/mineres-language/mineres-interpreter/tree/main/data/grammar) (Especificação Formal)
Contém o arquivo [**`mineres.gmr`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/grammar/mineres.gmr), que documenta a gramática da linguagem.
* **Finalidade:** Serve como o manual de referência para a implementação das regras de produção e precedência de operadores no [**Parser**](https://github.com/mineres-language/mineres-interpreter/tree/main/src/parser). É a representação abstrata da sintaxe da linguagem.

### 2. [/input](https://github.com/mineres-language/mineres-interpreter/tree/main/data/input) (Suíte de Testes)
Espaço destinado aos scripts escritos em Minerês (extensão `.uai`) utilizados para validar o interpretador.
* [**`entrada.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/input/entrada.uai): Script padrão consumido pelo orquestrador (`main.py`). Edite este arquivo para testar diferentes programas.
* [**`tests_erros.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/input/tests_erros.uai): Casos organizados em três seções — erros de execução (divisão por zero, variável não declarada), erros semânticos de tipo (detectados pelo Parser), e regressões de bug (comportamentos anteriormente incorretos, agora corrigidos).
* [**`tests_lista_codigo_intermediario.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/input/tests_lista_codigo_intermediario.uai): Exercícios da lista do professor, cobrindo expressões, condicionais, laços e algoritmos clássicos (Fibonacci, fatorial, primo, palíndromo, etc.).

### 3. [`/output`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/output) (Resultados do Pipeline)
Armazena as saídas geradas após a análise do código-fonte.
* [**`saida.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/output/saida.uai): Dump formatado da análise léxica (lista de tokens), permitindo verificar se o **Lexer** mapeou corretamente os lexemas, códigos, linhas e colunas.
* [**`saida_ir.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/output/saida_ir.uai): Lista de tuplas do **Código Intermediário** gerado pelo Parser, no formato `(op, a, b, c)`. Útil para inspecionar o IR antes da execução na máquina virtual.

---

## Procedimento de Teste

Para realizar novos testes no interpretador:
1. Adicione ou edite um arquivo `.uai` em [`data/input/`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/input).
2. Verifique se o caminho no [`main.py`](https://github.com/mineres-language/mineres-interpreter/blob/main/src/main.py) aponta para o arquivo que deseja testar.
3. Execute o interpretador e confira o log de saída no terminal e o arquivo gerado em [`data/output/`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/output).

---

[Voltar para a Documentação Principal](../README.md)