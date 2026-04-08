import sys
from tokens import *

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0  # Nosso "dedo" apontando para o token atual na lista
        self.tamanho = len(tokens)

    # -------------------------------------------------------------------------
    # Helpers de Navegação e Controle
    # -------------------------------------------------------------------------

    def token_atual(self):
        """Retorna a tupla do token atual. Se a lista acabar, retorna um EOF fictício."""
        if self.pos < self.tamanho:
            return self.tokens[self.pos]
        
        # Prevenção para não estourar erro de índice de lista (IndexError)
        ultimo = self.tokens[-1] if self.tamanho > 0 else ("", "EOF", 1, 1)
        return ("EOF", "EOF", ultimo[2], ultimo[3])

    def avanca(self):
        """Avança o ponteiro para o próximo token da lista."""
        if self.pos < self.tamanho:
            self.pos += 1

    def disparar_erro_sintatico(self, esperado: str, token_recebido: tuple):
        """Panic Mode: Aborta a execução no primeiro erro sintático encontrado."""
        lexema, codigo, linha, coluna = token_recebido
        
        print("\n[ERRO SINTÁTICO]")
        print(f"Linha: {linha}, Coluna: {coluna}")
        print(f"Esperava: {esperado}")
        print(f"Recebi  : '{lexema}'")
        print("Execução abortada.\n")
        sys.exit(1)

    def consome(self, codigo_esperado: int, nome_esperado_para_erro: str):
        """
        O Juiz: Verifica se o token atual é o que a gramática exige.
        Se for, engole o token e avança. Se não for, mata o programa.
        """
        atual = self.token_atual()
        
        if atual[1] == codigo_esperado:
            self.avanca()
        else:
            self.disparar_erro_sintatico(nome_esperado_para_erro, atual)

    # -------------------------------------------------------------------------
    # REGRAS DA GRAMÁTICA (Árvore de Decisão)
    # -------------------------------------------------------------------------

    def parse_function(self):
        """ <function*> -> 'bora_cumpade' 'main' '(' ')' <bloco> ; """
        self.consome(PR_BORA_CUMPADE, "'bora_cumpade'")
        self.consome(PR_MAIN, "'main'")
        self.consome(DEL_ABRE_PAR, "'('")
        self.consome(DEL_FECHA_PAR, "')'")
        self.parse_bloco()

    def parse_bloco(self):
        """ <bloco> -> 'simbora' <stmtList> 'cabo' ; """
        self.consome(DEL_SIMBORA, "'simbora'")
        self.parse_stmtList()
        self.consome(DEL_CABO, "'cabo'")

    def parse_stmtList(self):
        """ <stmtList> -> <stmt> <stmtList> | & ; """
        # ETAPA 1: Por enquanto, o bloco finge que está vazio (Lê o '&' / Lambda).
        # Implementaremos as validações de comandos de verdade na Etapa 2.
        pass

    # -------------------------------------------------------------------------
    # Ponto de Entrada
    # -------------------------------------------------------------------------

    def iniciar(self):
        if self.tamanho == 0:
            print("Nenhum token para analisar.")
            return

        # 1. A gramática diz que todo programa começa obrigatoriamente pela regra function
        self.parse_function()

        # 2. Se o programa acabou, não deve sobrar nenhum token "perdido" lá fora
        if self.pos < self.tamanho:
            self.disparar_erro_sintatico("Fim do arquivo (Nenhum código fora da main)", self.token_atual())

        print("\n[SUCESSO] Análise Sintática concluída! O esqueleto do programa está correto.")