# Módulo: Dados e Recursos (Data)

Este diretório centraliza o suporte do interpretador **Minerês**, separando a definição formal da linguagem e os conjuntos de testes da lógica de processamento presente no diretório `src/`.

---

## Estrutura de Conteúdo

### 1. [/grammar](https://github.com/mineres-language/mineres-interpreter/tree/main/data/grammar) (Especificação Formal)
Contém o arquivo [**`mineres.gmr`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/grammar/mineres.gmr), que documenta a gramática da linguagem.
* **Finalidade:** Serve como o manual de referência para a implementação das regras de produção e precedência de operadores no [**Parser**](https://github.com/mineres-language/mineres-interpreter/tree/main/src/parser). É a representação abstrata da sintaxe da linguagem.

### 2. [/input](https://github.com/mineres-language/mineres-interpreter/tree/main/data/input) (Suíte de Testes)
Espaço destinado aos scripts escritos em Minerês (extensão `.uai`) utilizados para validar o interpretador.
* [**`entrada.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/input/entrada.uai): Script padrão consumido pelo orquestrador (`main.py`).
* **`teste_1.uai` a `teste_5.uai`**: Casos de teste que cobrem diferentes cenários do interpretador, incluindo:
    * Declaração de variáveis e atribuições.
    * Estruturas de controle de fluxo (`uai_se`, `enquanto_tiver_trem`).
    * Operações lógicas, aritméticas e relacionais.
    * Validação de mensagens de erro sintático e léxico.

### 3. [`/output`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/output) (Resultados do Pipeline)
Armazena as saídas geradas após a análise do código-fonte.
* [**`saida.uai`**](https://github.com/mineres-language/mineres-interpreter/blob/main/data/output/saida.uai): Atualmente, armazena o dump formatado da análise léxica (Tokens), permitindo verificar se o **Lexer** mapeou corretamente os lexemas, códigos, linhas e colunas.

---

## Procedimento de Teste

Para realizar novos testes no interpretador:
1. Adicione ou edite um arquivo `.uai` em [`data/input/`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/input).
2. Verifique se o caminho no [`main.py`](https://github.com/mineres-language/mineres-interpreter/blob/main/src/main.py) aponta para o arquivo que deseja testar.
3. Execute o interpretador e confira o log de saída no terminal e o arquivo gerado em [`data/output/`](https://github.com/mineres-language/mineres-interpreter/tree/main/data/output).

---

[Voltar para a Documentação Principal](../README.md)