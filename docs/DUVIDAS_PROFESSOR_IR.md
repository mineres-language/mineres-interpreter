# Dúvidas sobre a Etapa 3: Geração de Código Intermediário

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

## 4. Distinção entre divisões `sob` e `/`

**Decisão tomada:**
- `sob` → `div` (divisão real, pode resultar em float)
- `/` → `divI` (divisão inteira)

**Pergunta:** certo?.

estourar erro se tiver divI de dois números não inteiros (divI ambos tem que ser int necessariamente)

---

dois chars somados vira string 'a' + 'a' = "aa"


---

and, or etc só pode ter operadores booleanos

4 < 5 vira true, vira boolean