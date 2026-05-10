# Dúvidas sobre a Etapa 3: Geração de Código Intermediário

## 1. `if` sem `else`: formato dos dois labels

**Professor:**
```
(if, condition, label1, label2)
```

Quando o `uai_se` tem `uai_senao`, o uso é:
- `label1` = início do bloco `then`
- `label2` = início do bloco `else`

**Mas e quando não tem `uai_senao`?**

**Decisão tomada:** gera um label "vazio" para o else (que aponta direto pro fim do if). Exemplo:

```mineres
uai_se (a < b) simbora oia_proce_ve("oi") uai cabo
```

Gera:
```
(less, t1, a, b)
(if, t1, L1, L2)        ← L2 é o "else vazio"
(label, L1, null, null)
(call, print, null, "oi")
(jump, L3, null, null)
(label, L2, null, null) ← else vazio (sem código)
(label, L3, null, null) ← fim
```

**Pergunta:** está correto, ou quando não tem else o `label2` deve apontar
diretamente pro fim, sem o label intermediário "vazio"?

---

## 2. Análise semântica de tipos

**Decisão tomada:** implementou somente verificação de **declaração** (variável
não declarada → erro; redeclaração → erro). Não vemos compatibilidade de
tipos em operações nem em atribuições.

Por exemplo, isso passa sem erro:
```mineres
trem_di_numeru x uai
trem_discrita s uai
x fica_assim_entao s uai          // int = string, sem erro
x fica_assim_entao "texto" uai     // int = literal string, sem erro
```

**Perguntas:**
- A análise semântica deve incluir checagem de tipos compatíveis?
- Se sim, há imposição implícitas permitidas (`int → float`)?
- Operações entre tipos diferentes (`int + string`) devem ser erro?
- Condições de `if`/`while`/`for` devem obrigatoriamente ser do tipo bool?

---

## 3. Valor inicial padrão para tipos sem default óbvio

**Decisão tomada:** quando uma variável é declarada sem inicializador, ela recebe:

| Tipo | Valor padrão |
|---|---|
| `trem_di_numeru` (int) | `0` |
| `trem_cum_virgula` (float) | `0.0` |
| `trem_discrita` (string) | `""` |
| `trem_discolhe` (bool) | `"eh"` (true) |
| `trosso` (char) | `"\0"` |

**Perguntas:**
- O bool deve ser inicializado como `eh` (true) ou `num_eh` (false)?
- O char deve ser `'\0'` ou outra coisa?
- Quer um valor específico, ou podemos definir?

---

## 4. Distinção entre divisões `sob` e `/`

**Decisão tomada:**
- `sob` → `div` (divisão real, pode resultar em float)
- `/` → `divI` (divisão inteira)

**Pergunta:** certo?.

---

## 5. Operador unário: formato da tupla

**Spec do professor:**
```
(uno, -, res, op1)
(uno, +, res, op2)
```

O segundo elemento é o **literal do operador** (`"+"` ou `"-"`), não um valor de
posição. Isso é diferente do padrão `(op, res, a, b)` dos outros operadores.

**Decisão tomada:** fizemos literalmente. Exemplo:
```mineres
trem_di_numeru x uai
x fica_assim_entao -5 uai
```
Gera:
```
(uno, "-", t1, 5)
(att, x, t1, null)
```

**Pergunta:** certo?

---

## 6. `break` (`para_o_trem`) e `continue` (`toca_o_trem`) em `dependenu`

**Decisão tomada:** dentro de `dependenu`, o `para_o_trem` foi tratado como
"sair do switch" (pula pro fim do `dependenu`). Já o `toca_o_trem` no switch
não faz sentido, mas se for usado, vai pular pra junto do break
(também sai). Geralmente, em C, o `continue` em `switch` afeta o loop externo.

**Pergunta:**
- O `para_o_trem` dentro de `dependenu` deve sair do switch?
- O `toca_o_trem` dentro de `dependenu` deve afetar um loop externo (se houver)?
- Ou esses comandos só funcionam em loops `enquanto_tiver_trem` / `roda_esse_trem`?

---

## 7. Operadores lógicos com curto-circuito?

**Decisão tomada:** os operadores `tamem` (and), `quarque_um` (or), `um_o_oto`
(xor) geram tuplas simples como qualquer operação binária:

```
(and, t3, t1, t2)
```

Não implementamos curto-circuito (em C, `false && f()` não chama `f()`).

**Pergunta:** precisa de curto-circuito?