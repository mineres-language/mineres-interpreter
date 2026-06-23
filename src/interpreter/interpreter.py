import sys

class Interpretador:
    def __init__(self, codigo_ir: list):
        self.codigo = codigo_ir
        
        # "Memória RAM". Variáveis serão criadas aqui na primeira atribuição.
        self.variaveis = {} 
        
        # Dicionário de rotas para os desvios de fluxo (Jumps/Ifs)
        self.labels = {}
        
        # Ponteiro de Instrução
        self.ip = 0 

    def disparar_erro(self, mensagem: str):
        print(f"\n[ERRO INTERPRETADOR]\nFalha na instrução {self.ip}")
        print(f"Detalhe: {mensagem}")
        print("Execução da Máquina Virtual abortada.\n")
        sys.exit(1)

    def mapear_labels(self):
        """Pré-processamento: salva o índice de cada label antes de executar."""
        for i, instrucao in enumerate(self.codigo):
            op = instrucao[0]
            if op == "label":
                nome_label = instrucao[1]
                self.labels[nome_label] = i

    def obter_valor(self, operando):
        """Busca valor real de um operando: busca na memória se for variável, retorna direto se for literal."""
        if operando is None or operando == "null":
            return None
            
        if isinstance(operando, str) and operando.startswith('@'):
            if operando in self.variaveis:
                return self.variaveis[operando]
            elif operando.startswith('@_t'):
                nome_limpo = operando[1:]
                self.disparar_erro(f"Temporária '{nome_limpo}' acessada antes de ser inicializada.")
            else:
                # Se não for uma variável declarada nem temporária,
                # trata-se de uma string literal do usuário que começa com '@'.
                return operando
                 
        return operando

    def executar(self):
        if not self.codigo:
            print("Nenhum código intermediário para executar.")
            return

        # 1. Prepara as rotas de salto
        self.mapear_labels()

        print("" + "="*40)
        print("           INICIANDO  EXECUÇÃO ")
        print("="*40 + "\n")

        # 2. Inicia o ciclo de máquina
        while self.ip < len(self.codigo):
            instrucao = self.codigo[self.ip]
            op = instrucao[0]
            
            # O ponteiro sempre avança. Instruções de Jump vão sobrescrever isso se necessário.
            self.ip += 1

            if op == "label":
                pass # Labels não fazem nada durante a execução, apenas marcam posição
                
            elif op == "att":
                # ("att", destino, valor_origem, None)
                dest = instrucao[1]
                val = self.obter_valor(instrucao[2])
                self.variaveis[dest] = val

            # ---------------------------------------------------------
            # ENTRADA E SAÍDA (I/O)
            # ---------------------------------------------------------
            elif op == "call":
                func = instrucao[1]
                if func == "print":
                    # O parser gera ("call", "print", var, None) ou ("call", "print", None, literal)
                    # Verificamos qual posição contém a informação

                    if instrucao[3] is not None:
                        valor = instrucao[3]
                    else:
                        valor = self.obter_valor(instrucao[2])
                    
                    # Removemos aspas duplas de strings literais apenas na hora de imprimir
                    if isinstance(valor, str) and valor.startswith('"') and valor.endswith('"'):
                        valor = valor[1:-1]
                    print(valor)
                    
                elif func == "read":
                    # ("call", "read", destino, tipo_nome)
                    dest = instrucao[2]
                    tipo_nome = instrucao[3]
                    entrada = input()

                    if tipo_nome == "trem_di_numeru":
                        try:
                            entrada = int(entrada)
                        except ValueError:
                            self.disparar_erro(
                                f"Entrada inválida: '{entrada}' não é um número inteiro (trem_di_numeru)."
                            )
                    elif tipo_nome == "trem_cum_virgula":
                        try:
                            entrada = float(entrada)
                        except ValueError:
                            self.disparar_erro(
                                f"Entrada inválida: '{entrada}' não é um número real (trem_cum_virgula)."
                            )
                    # trem_discrita e trosso: mantém como string

                    self.variaveis[dest] = entrada

            # ---------------------------------------------------------
            # UNIDADE LÓGICA E MATEMÁTICA (ALU)
            # ---------------------------------------------------------
            elif op in {"add", "sub", "mult", "div", "divI", "mod", "and", "or", "xor", "less", "leq", "gret", "geq", "eq", "dif"}:
                # Operações Binárias: (op, destino, op1, op2)
                dest = instrucao[1]
                v1 = self.obter_valor(instrucao[2])
                v2 = self.obter_valor(instrucao[3])
                res = None

                # Tratamento de literais booleanos para operadores lógicos
                if op in {"and", "or", "xor"}:
                    b1 = True if v1 == "eh" else (False if v1 == "num_eh" else bool(v1))
                    b2 = True if v2 == "eh" else (False if v2 == "num_eh" else bool(v2))
                    if op == "and":  raw = b1 and b2
                    elif op == "or": raw = b1 or b2
                    else:            raw = b1 ^ b2
                    res = "eh" if raw else "num_eh"
                else:
                    try:
                        # Operações Aritméticas
                        if op == "add": res = v1 + v2
                        elif op == "sub": res = v1 - v2
                        elif op == "mult": res = v1 * v2
                        elif op == "div":
                            if v2 == 0: self.disparar_erro("Divisão real por zero.")
                            res = v1 / v2
                        elif op == "divI":
                            if v2 == 0: self.disparar_erro("Divisão inteira por zero.")
                            res = v1 // v2
                        elif op == "mod":
                            if v2 == 0: self.disparar_erro("Módulo (resto) por zero.")
                            res = v1 % v2

                        # Operações Relacionais — sempre produzem "eh" ou "num_eh"
                        elif op == "less": res = "eh" if v1 < v2  else "num_eh"
                        elif op == "leq":  res = "eh" if v1 <= v2 else "num_eh"
                        elif op == "gret": res = "eh" if v1 > v2  else "num_eh"
                        elif op == "geq":  res = "eh" if v1 >= v2 else "num_eh"
                        elif op == "eq":   res = "eh" if v1 == v2 else "num_eh"
                        elif op == "dif":  res = "eh" if v1 != v2 else "num_eh"
                    except TypeError:
                        self.disparar_erro("Erro de tipo em tempo de execução: Tipos incompatíveis para a operação.")

                self.variaveis[dest] = res

            elif op == "uno":
                # Operador Unário Matemático (+, -): ("uno", sinal, destino, origem)
                sinal = instrucao[1]
                dest = instrucao[2]
                v = self.obter_valor(instrucao[3])
                try:
                    self.variaveis[dest] = v if sinal == "+" else -v
                except TypeError:
                    self.disparar_erro("Erro de tipo em tempo de execução: Operador unário incompatível com o tipo.")

            elif op == "not":
                # Operador Unário Lógico (!): ("not", destino, origem, None)
                dest = instrucao[1]
                v = self.obter_valor(instrucao[2])

                if v == "eh": v = True
                elif v == "num_eh": v = False

                self.variaveis[dest] = "eh" if not bool(v) else "num_eh"

            # ---------------------------------------------------------
            # CONTROLE DE FLUXO (JUMPS E IF)
            # ---------------------------------------------------------
            elif op == "if":
                # ("if", condicao, label_true, label_false)
                cond_val = self.obter_valor(instrucao[1])
                
                # Tradução nativa dos booleanos do Minerês
                if cond_val == "eh": cond_val = True
                elif cond_val == "num_eh": cond_val = False
                
                alvo = instrucao[2] if cond_val else instrucao[3]
                
                if alvo not in self.labels:
                    self.disparar_erro(f"Label '{alvo}' não encontrado.")
                
                # O salto (Jump) acontece manipulando o Ponteiro (ip)
                self.ip = self.labels[alvo]

            elif op == "jump":
                # ("jump", label_alvo, None, None)
                alvo = instrucao[1]
                if alvo not in self.labels:
                    self.disparar_erro(f"Label '{alvo}' não encontrado.")
                self.ip = self.labels[alvo]

            else:
                self.disparar_erro(f"Operação desconhecida pelo interpretador: '{op}'")

        print("\n" + "="*40)
        print("             FIM DA EXECUÇÃO ")
        print("="*40 + "\n")