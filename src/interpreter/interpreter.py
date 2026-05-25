import sys

class Interpretador:
    def __init__(self, codigo_ir: list):
        self.codigo = codigo_ir
        
        # A nossa "Memória RAM". Variáveis serão criadas aqui na primeira atribuição.
        self.variaveis = {} 
        
        # Dicionário de rotas para os desvios de fluxo (Jumps/Ifs)
        self.labels = {}
        
        # Ponteiro de Instrução (Instruction Pointer)
        self.ip = 0 

    def disparar_erro(self, mensagem: str):
        """ Interrompe a execução exibindo um erro semântico amigável. """
        print(f"\n[ERRO INTERPRETADOR]\nFalha na instrução {self.ip}")
        print(f"Detalhe: {mensagem}")
        print("Execução da Máquina Virtual abortada.\n")
        sys.exit(1)

    def mapear_labels(self):
        """ 
        Passo 2: Pré-processamento. 
        Varre o código salvando o índice (linha) de cada Label antes da execução real.
        """
        for i, instrucao in enumerate(self.codigo):
            op = instrucao[0]
            if op == "label":
                nome_label = instrucao[1]
                self.labels[nome_label] = i

    def obter_valor(self, operando):
        """ 
        Busca o valor real de um operando. 
        Se for o nome de uma variável, busca na memória. Se for literal, retorna direto.
        """
        if operando is None or operando == "null":
            return None
            
        if isinstance(operando, str) and operando.startswith('@'):
            if operando in self.variaveis:
                return self.variaveis[operando]
            else:
                nome_limpo = operando[1:]
                self.disparar_erro(f"Variável ou temporária '{nome_limpo}' acessada antes de ser inicializada.")
                 
        return operando

    def executar(self):
        """ O laço principal da Máquina Virtual. """
        if not self.codigo:
            print("Nenhum código intermediário para executar.")
            return

        # 1. Prepara as rotas de salto
        self.mapear_labels()

        print("\n" + "="*40)
        print(" INICIANDO EXECUÇÃO (MÁQUINA VIRTUAL) ")
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
                    # ("call", "read", destino, None)
                    dest = instrucao[2]
                    entrada = input()
                    
                    # Tenta converter a entrada do teclado para o tipo numérico correto
                    try:
                        if '.' in entrada:
                            entrada = float(entrada)
                        else:
                            entrada = int(entrada)
                    except ValueError:
                        pass # Se falhar, mantém como string
                        
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
                    
                # Operações Relacionais e Lógicas
                elif op == "and": res = bool(v1 and v2)
                elif op == "or":  res = bool(v1 or v2)
                elif op == "xor": res = bool(v1 ^ v2)
                elif op == "less": res = v1 < v2
                elif op == "leq":  res = v1 <= v2
                elif op == "gret": res = v1 > v2
                elif op == "geq":  res = v1 >= v2
                elif op == "eq":   res = v1 == v2
                elif op == "dif":  res = v1 != v2

                self.variaveis[dest] = res

            elif op == "uno":
                # Operador Unário Matemático (+, -): ("uno", sinal, destino, origem)
                sinal = instrucao[1]
                dest = instrucao[2]
                v = self.obter_valor(instrucao[3])
                self.variaveis[dest] = v if sinal == "+" else -v

            elif op == "not":
                # Operador Unário Lógico (!): ("not", destino, origem, None)
                dest = instrucao[1]
                v = self.obter_valor(instrucao[2])
                
                if v == "eh": v = True
                elif v == "num_eh": v = False
                
                self.variaveis[dest] = not bool(v)

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
        print(" FIM DA EXECUÇÃO (MÁQUINA VIRTUAL) ")
        print("="*40 + "\n")