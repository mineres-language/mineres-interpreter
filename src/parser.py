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
    # Regras da Gramática (Árvore de Decisão)
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
        atual = self.token_atual()[1]
        
        # O conjunto FIRST de todos os comandos que faremos (por enquanto, tipos de variaveis e IO)
        primeiros_de_stmt = [
            PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO,
            PR_XOVE, PR_OIA_PROCE_VE
        ]
        
        if atual in primeiros_de_stmt:
            self.parse_stmt()
            self.parse_stmtList() # Chama a si mesma para ver se tem mais comandos na linha de baixo
        elif atual == DEL_CABO:
            # Encontrou o final do bloco! Esse é o Épsilon / Vazio (&) da gramática.
            # Apenas retornamos (subimos na árvore) sem consumir nada.
            return 
        else:
            self.disparar_erro_sintatico("Início de comando válido ou 'cabo'", self.token_atual())

    def parse_stmt(self):
        """ <stmt> -> <ioStmt> | <declaration> | ... (outros no futuro) """
        atual = self.token_atual()[1]
        
        tipos_variaveis = [PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO]
        
        if atual in tipos_variaveis:
            self.parse_declaration()
        elif atual in [PR_XOVE, PR_OIA_PROCE_VE]:
            self.parse_ioStmt()
        else:
            self.disparar_erro_sintatico("Comando válido", self.token_atual())
    
    # -------------------------------------------------------------------------
    # Declaração de Variáveis
    # -------------------------------------------------------------------------

    def parse_declaration(self):
        """ <declaration> -> <type> <identList> 'uai' ; """
        self.parse_type()
        self.parse_identList()
        self.consome(DEL_UAI, "'uai'")

    def parse_type(self):
        """ <type> -> 'trem_di_numeru' | 'trem_cum_virgula' | 'trem_discrita' | 'trem_discolhe' | 'trosso' """
        atual = self.token_atual()[1]
        tipos_validos = {
            PR_TREM_DI_NUMERU: "'trem_di_numeru'",
            PR_TREM_CUM_VIRGULA: "'trem_cum_virgula'",
            PR_TREM_DISCRITA: "'trem_discrita'",
            PR_TREM_DISCOLHE: "'trem_discolhe'",
            PR_TROSSO: "'trosso'"
        }
        
        if atual in tipos_validos:
            self.consome(atual, tipos_validos[atual])
        else:
            self.disparar_erro_sintatico("Tipo de variável", self.token_atual())

    def parse_identList(self):
        """ <identList> -> 'IDENT' <restoIdentList> """
        self.consome(IDENTIFICADOR, "Identificador (nome de variável)")
        self.parse_restoIdentList()

    def parse_restoIdentList(self):
        """ <restoIdentList> -> ',' 'IDENT' <restoIdentList> | & ; """
        atual = self.token_atual()[1]
        if atual == DEL_VIRGULA:
            self.consome(DEL_VIRGULA, "','")
            self.consome(IDENTIFICADOR, "Identificador")
            self.parse_restoIdentList()
        else:
            # Não tem vírgula? Então a lista acabou (Regra & / Lambda)
            return
    
    # -------------------------------------------------------------------------
    # I/O (Prints e Inputs)
    # -------------------------------------------------------------------------
    
    def parse_ioStmt(self):
        """ <ioStmt> -> 'xove' '(' <type> ',' 'IDENT' ')' 'uai' | 'oia_proce_ve' '(' <outList> ')' 'uai' """
        atual = self.token_atual()[1]
        
        if atual == PR_XOVE: # Input
            self.consome(PR_XOVE, "'xove'")
            self.consome(DEL_ABRE_PAR, "'('")
            self.parse_type()
            self.consome(DEL_VIRGULA, "','")
            self.consome(IDENTIFICADOR, "Identificador")
            self.consome(DEL_FECHA_PAR, "')'")
            self.consome(DEL_UAI, "'uai'")
            
        elif atual == PR_OIA_PROCE_VE: # Output/Print
            self.consome(PR_OIA_PROCE_VE, "'oia_proce_ve'")
            self.consome(DEL_ABRE_PAR, "'('")
            self.parse_outList()
            self.consome(DEL_FECHA_PAR, "')'")
            self.consome(DEL_UAI, "'uai'")

    def parse_outList(self):
        """ <outList> -> <out> <restoOutList> """
        self.parse_out()
        self.parse_restoOutList()

    def parse_out(self):
        """ <out> -> <fatorZin> """
        self.parse_fatorZin()

    def parse_restoOutList(self):
        """ <restoOutList> -> ',' <out> <restoOutList> | & ; """
        if self.token_atual()[1] == DEL_VIRGULA:
            self.consome(DEL_VIRGULA, "','")
            self.parse_out()
            self.parse_restoOutList()
        else:
            return # Vazio / Epsilon

    def parse_fatorZin(self):
        """ <fatorZin> -> 'STR' | 'IDENT' | 'NUMint' | 'NUMfloat' | 'valorBooleano' | 'valorChar' """
        atual = self.token_atual()[1]
        
        # Tudo que pode ser impresso/passado
        literais_validos = [
            LIT_STRING, IDENTIFICADOR, LIT_NUM_INT, LIT_NUM_FLOAT, 
            LIT_CHAR, PR_EH, PR_NUM_EH
        ]
        
        if atual in literais_validos:
            # Consome o que quer que seja e avança
            self.consome(atual, "Valor Literal ou Variável")
        else:
            self.disparar_erro_sintatico("Valor para impressão", self.token_atual())

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