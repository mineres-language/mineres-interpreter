# Módulo: Interpretador (Máquina Virtual)

O **Interpretador** é a etapa final do pipeline. Ele recebe a lista de tuplas do **[Código Intermediário](./ir.md)** e as executa diretamente, simulando uma **Máquina Virtual** de pilha simples.

---

## Detalhes da Implementação

O Interpretador opera sobre o IR já gerado, percorrendo as tuplas sequencialmente. O controle de fluxo (saltos, condicionais) é implementado manipulando um **Ponteiro de Instrução** (`ip`), que aponta para o índice da tupla atual na lista.

### Estrutura Interna

| Atributo     | Tipo   | Finalidade                                                          |
|--------------|--------|---------------------------------------------------------------------|
| `codigo`     | list   | A lista de tuplas do IR recebida do Parser                          |
| `variaveis`  | dict   | Memória de execução: mapeia `@nome` → valor atual                   |
| `labels`     | dict   | Tabela de roteamento: mapeia `"L1"` → índice da tupla na lista      |
| `ip`         | int    | Ponteiro de Instrução (*Instruction Pointer*) — índice atual        |

---

## Pipeline de Execução

A execução ocorre em dois passos:

**1. Pré-processamento (`mapear_labels`):**
Varre todo o IR e registra a posição de cada `("label", ...)` no dicionário `labels`. Isso permite saltos em O(1) durante a execução.

**2. Ciclo de Máquina (`executar`):**
Itera sobre as tuplas enquanto `ip < len(codigo)`. A cada iteração, `ip` avança automaticamente; instruções de salto sobrescrevem esse avanço para redirecionar o fluxo.

---

## Conjunto de Instruções

### Atribuição
```
("att", @destino, valor_ou_@origem, null)
```
Armazena `valor` (ou o valor de `@origem`) na variável `@destino` em memória.

### Entrada / Saída
```
("call", "print", @var, null)      // imprime valor da variável
("call", "print", null,  "literal") // imprime string literal
("call", "read",  @dest, null)     // lê do teclado → converte para int/float se possível
```

### Operações Aritméticas
```
("add",  @dest, @op1, @op2)    // +
("sub",  @dest, @op1, @op2)    // -
("mult", @dest, @op1, @op2)    // veiz (*)
("div",  @dest, @op1, @op2)    // sob (divisão real)
("divI", @dest, @op1, @op2)    // / (divisão inteira)
("mod",  @dest, @op1, @op2)    // %
```
> Divisão por zero em `div`, `divI` e `mod` dispara erro de execução.

### Operador Unário
```
("uno", "+", @dest, @origem)
("uno", "-", @dest, @origem)
```

### Operações Lógicas
```
("and", @dest, @op1, @op2)    // tamem
("or",  @dest, @op1, @op2)    // quarque_um
("xor", @dest, @op1, @op2)    // um_o_oto
("not", @dest, @origem, null) // vam_marca
```
Os valores `"eh"` e `"num_eh"` do Minerês são convertidos para `True`/`False` do Python antes da operação.

### Operações Relacionais
```
("less", @dest, @op1, @op2)   // <
("leq",  @dest, @op1, @op2)   // <=
("gret", @dest, @op1, @op2)   // >
("geq",  @dest, @op1, @op2)   // >=
("eq",   @dest, @op1, @op2)   // mema_coisa
("dif",  @dest, @op1, @op2)   // neh_nada
```
O resultado é um booleano Python (`True`/`False`), compatível com a lógica de salto do `if`.

### Controle de Fluxo
```
("label", "L1", null, null)          // marca posição — não faz nada em tempo de execução
("jump",  "L1", null, null)          // salta incondicionalmente para L1
("if",    @cond, "L_true", "L_false") // salta para L_true se cond for verdadeiro, senão L_false
```
A instrução `if` aceita `"eh"` / `"num_eh"` além de booleanos Python.

---

## Resolução de Operandos (`obter_valor`)

Antes de executar qualquer operação, o interpretador resolve o valor real de cada operando:

- `None` / `"null"` → retorna `None`
- String começando com `@` → busca na memória (`self.variaveis`)
- Qualquer outro valor → retorna diretamente (literal numérico, string, booleano)

---

## Tratamento de Erros em Execução

Erros em tempo de execução são reportados com o índice da instrução falha:

```
[ERRO INTERPRETADOR]
Falha na instrução 12
Detalhe: Divisão inteira por zero.
Execução da Máquina Virtual abortada.
```

Situações que geram erro:
- Divisão real, inteira ou módulo por zero
- Tipo incompatível para operação aritmética ou unária (ex: somar strings na VM)
- Label de salto não encontrado no dicionário de rotas

---

[Voltar para a Documentação Principal](../README.md)
