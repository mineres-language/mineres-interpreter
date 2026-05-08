import sys
from lexer.tokens import *

PRIMEIROS_DE_STMT = {
    PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO,
    PR_XOVE, PR_OIA_PROCE_VE, 
    PR_UAI_SE, PR_ENQUANTO, PR_RODA_ESSE_TREM, PR_DEPENDENU,
    DEL_SIMBORA, PR_PARA_O_TREM, PR_TOCA_O_TREM, DEL_UAI,
    IDENTIFICADOR, LIT_NUM_INT, LIT_NUM_HEX, LIT_NUM_OCT, LIT_NUM_FLOAT, LIT_STRING, LIT_CHAR, PR_EH, PR_NUM_EH
}

class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0 
        self.tamanho = len(tokens)

    # -------------------------------------------------------------------------
    # Helpers de Navegação e Controle
    # -------------------------------------------------------------------------

    def token_atual(self):
        if self.pos < self.tamanho:
            return self.tokens[self.pos]
        
        # prevenção para não estourar erro de índice de lista (IndexError)
        ultimo = self.tokens[-1] if self.tamanho > 0 else ("", "EOF", 1, 1)
        return ("EOF", "EOF", ultimo[2], ultimo[3])

    def avanca(self):
        if self.pos < self.tamanho:
            self.pos += 1

    def disparar_erro_sintatico(self, esperado: str, token_recebido: tuple):
        lexema, codigo, linha, coluna = token_recebido
        
        print("\n[ERRO SINTÁTICO]")
        print(f"Linha: {linha}, Coluna: {coluna}")
        print(f"Esperava: {esperado}")
        print(f"Recebi  : '{lexema}'")
        print("Execução abortada.\n")
        sys.exit(1)

    def consome(self, codigo_esperado: int):
        # recebe apenas o código, o nome do erro é buscado
        atual = self.token_atual()
        
        if atual[1] == codigo_esperado:
            self.avanca()
        else:
            # busca no dicionário reverso, se não achar, usa um genérico
            esperado = NOMES_TOKENS.get(codigo_esperado, f"Token {codigo_esperado}")
            self.disparar_erro_sintatico(esperado, atual)

    # -------------------------------------------------------------------------
    # Regras da Gramática (Árvore de Decisão)
    # -------------------------------------------------------------------------

    def parse_function(self):
        """ <function*> -> 'bora_cumpade' 'main' '(' ')' <bloco> ; """
        self.consome(PR_BORA_CUMPADE)
        self.consome(PR_MAIN)
        self.consome(DEL_ABRE_PAR)
        self.consome(DEL_FECHA_PAR)
        self.parse_bloco()

    def parse_bloco(self):
        """ <bloco> -> 'simbora' <stmtList> 'cabo' ; """
        self.consome(DEL_SIMBORA)
        self.parse_stmtList()
        self.consome(DEL_CABO)

    def parse_stmtList(self):
        """ <stmtList> -> <stmt> <stmtList> | & ; """
        atual = self.token_atual()[1]
        
        if atual in PRIMEIROS_DE_STMT:
            self.parse_stmt()
            self.parse_stmtList()
        elif atual == DEL_CABO:
            return
        else:
            esperados = "sintaxe de comando (ex: 'uai_se', 'enquanto_tiver_trem', 'trem_di_numeru', 'xove'...) ou fechamento 'cabo'"
            self.disparar_erro_sintatico(esperados, self.token_atual())

    def parse_stmt(self):
        atual = self.token_atual()[1]
        tipos_variaveis = {PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO} # Hash rápida O(1)
        
        if atual in tipos_variaveis:
            self.parse_declaration()
        elif atual in {PR_XOVE, PR_OIA_PROCE_VE}:
            self.parse_ioStmt()
        elif atual == PR_UAI_SE:
            self.parse_ifStmt()
        elif atual == PR_ENQUANTO:
            self.parse_whileStmt()
        elif atual == PR_RODA_ESSE_TREM:
            self.parse_forStmt()
        elif atual == PR_DEPENDENU:
            self.parse_caseStmt()
        elif atual == DEL_SIMBORA:
            self.parse_bloco()
        elif atual == PR_PARA_O_TREM:
            self.consome(PR_PARA_O_TREM)
            self.consome(DEL_UAI)
        elif atual == PR_TOCA_O_TREM:
            self.consome(PR_TOCA_O_TREM)
            self.consome(DEL_UAI)
        elif atual in [DEL_UAI, DEL_PONTO_VIRGULA]:
            self.consome(DEL_UAI)
        else:
            self.parse_atrib()
            self.consome(DEL_UAI)

    # -------------------------------------------------------------------------
    # Declaração de Variáveis
    # -------------------------------------------------------------------------

    def parse_declaration(self):
        """ <declaration> -> <type> <identList> 'uai' ; """
        self.parse_type()
        self.parse_identList()
        self.consome(DEL_UAI)

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
            self.consome(atual)
        else:
            self.disparar_erro_sintatico("Tipo de variável", self.token_atual())

    def parse_identList(self):
        """ <identList> -> 'IDENT' <restoIdentList> """
        self.consome(IDENTIFICADOR)
        self.parse_restoIdentList()

    def parse_restoIdentList(self):
        """ <restoIdentList> -> ',' 'IDENT' <restoIdentList> | & ; """
        atual = self.token_atual()[1]
        if atual == DEL_VIRGULA:
            self.consome(DEL_VIRGULA)
            self.consome(IDENTIFICADOR)
            self.parse_restoIdentList()
        else:
            return
    
    # -------------------------------------------------------------------------
    # I/O (Prints e Inputs)
    # -------------------------------------------------------------------------

    def parse_ioStmt(self):
        """ <ioStmt> -> 'xove' '(' <type> ',' 'IDENT' ')' 'uai' | 'oia_proce_ve' '(' <outList> ')' 'uai' """
        atual = self.token_atual()[1]
        
        if atual == PR_XOVE: # Input
            self.consome(PR_XOVE)
            self.consome(DEL_ABRE_PAR)
            self.parse_type()
            self.consome(DEL_VIRGULA)
            self.consome(IDENTIFICADOR)
            self.consome(DEL_FECHA_PAR)
            self.consome(DEL_UAI)
            
        elif atual == PR_OIA_PROCE_VE: 
            self.consome(PR_OIA_PROCE_VE)
            self.consome(DEL_ABRE_PAR)
            self.parse_outList()
            self.consome(DEL_FECHA_PAR)
            self.consome(DEL_UAI)

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
            self.consome(DEL_VIRGULA)
            self.parse_out()
            self.parse_restoOutList()
        else:
            return 

    def parse_fatorZin(self):
        """ <fatorZin> -> 'STR' | 'IDENT' | 'NUMint' | 'NUMfloat' | 'valorBooleano' | 'valorChar' """
        atual = self.token_atual()[1]
        
        literais_validos = [
            LIT_STRING, IDENTIFICADOR, LIT_NUM_INT, LIT_NUM_HEX, 
            LIT_NUM_OCT, LIT_NUM_FLOAT, LIT_CHAR, PR_EH, PR_NUM_EH
        ]
        
        if atual in literais_validos:
            self.consome(atual)
        else:
            self.disparar_erro_sintatico("Valor para impressão", self.token_atual())

    # -------------------------------------------------------------------------
    # Estruturas de Controle
    # -------------------------------------------------------------------------
    
    def parse_ifStmt(self):
        """ <ifStmt> -> 'uai_se' '(' <expr> ')' <stmt> <elsePart> ; """
        self.consome(PR_UAI_SE)
        self.consome(DEL_ABRE_PAR)
        self.parse_expr()
        self.consome(DEL_FECHA_PAR)
        self.parse_stmt()
        self.parse_elsePart()

    def parse_elsePart(self):
        """ <elsePart> -> 'uai_senao' <stmt> | & ; """
        if self.token_atual()[1] == PR_UAI_SENAO:
            self.consome(PR_UAI_SENAO)
            self.parse_stmt()
        else:
            return 

    def parse_whileStmt(self):
        """ <whileStmt> -> 'enquanto_tiver_trem' '(' <expr> ')' <stmt> ; """
        self.consome(PR_ENQUANTO)
        self.consome(DEL_ABRE_PAR)
        self.parse_expr()
        self.consome(DEL_FECHA_PAR)
        self.parse_stmt()

    def parse_forStmt(self):
        """ <forStmt> -> 'roda_esse_trem' '(' <optExpr> ';' <optExpr> ';' <optExpr> ')' <stmt> ; """
        self.consome(PR_RODA_ESSE_TREM)
        self.consome(DEL_ABRE_PAR)
        self.parse_optExpr()
        self.consome(DEL_PONTO_VIRGULA)
        self.parse_optExpr()
        self.consome(DEL_PONTO_VIRGULA)
        self.parse_optExpr()
        self.consome(DEL_FECHA_PAR)
        self.parse_stmt()

    def parse_optExpr(self):
        """ <optExpr> -> <atrib> | & ; """
        atual = self.token_atual()[1]

        if atual in [DEL_PONTO_VIRGULA, DEL_FECHA_PAR]:
            return
        else:
            self.parse_atrib()

    def parse_caseStmt(self):
        """ <caseStmt> -> 'dependenu' '(' 'IDENT' ')' 'simbora' <dosCasos> 'cabo' ; """
        self.consome(PR_DEPENDENU)
        self.consome(DEL_ABRE_PAR)
        self.consome(IDENTIFICADOR)
        self.consome(DEL_FECHA_PAR)
        self.consome(DEL_SIMBORA)
        self.parse_dosCasos()
        self.consome(DEL_CABO)

    def parse_dosCasos(self):
        """ <dosCasos> -> <doCaso> <restoDosCasos> """
        self.parse_doCaso()
        self.parse_restoDosCasos()

    def parse_doCaso(self):
        """ <doCaso> -> 'du_casu' <fatorZin> ':' <stmt> """
        self.consome(PR_DU_CASU)
        self.parse_fatorZin()
        self.consome(DEL_DOIS_PONTOS)
        self.parse_stmt()

    def parse_restoDosCasos(self):
        """ <restoDosCasos> -> <doCaso><restoDosCasos> | 'uai_so' ':' <stmt> | & """
        atual = self.token_atual()[1]
        
        if atual == PR_DU_CASU:
            self.parse_doCaso()
            self.parse_restoDosCasos()
        
        elif atual == PR_UAI_SO:
            self.consome(PR_UAI_SO)
            self.consome(DEL_DOIS_PONTOS)
            self.parse_stmt()

        else:
            return 
        
    # -------------------------------------------------------------------------
    # Expressões Matemáticas e Lógicas
    # -------------------------------------------------------------------------

    def parse_expr(self):
        """ <expr> -> <atrib> ; """
        self.parse_atrib()

    def parse_atrib(self):
        """ <atrib> -> <or> <restoAtrib> ; """
        self.parse_or()
        self.parse_restoAtrib()

    def parse_restoAtrib(self):
        """ <restoAtrib> -> 'fica_assim_entao' <atrib> | & ; """
        if self.token_atual()[1] == OP_FICA_ASSIM_ENTAO:
            self.consome(OP_FICA_ASSIM_ENTAO)
            self.parse_atrib()

    def parse_or(self):
        """ <or> -> <xor> <restoOr> ; """
        self.parse_xor()
        self.parse_restoOr()

    def parse_restoOr(self):
        """ <restoOr> -> 'quarque_um' <xor> <restoOr> | & ; """
        if self.token_atual()[1] == OP_QUARQUE_UM:
            self.consome(OP_QUARQUE_UM)
            self.parse_xor()
            self.parse_restoOr()

    def parse_xor(self):
        """ <xor> -> <and> <restoXor> ; """
        self.parse_and()
        self.parse_restoXor()

    def parse_restoXor(self):
        """ <restoXor> -> 'um_o_oto' <and> <restoXor> | & ; """
        if self.token_atual()[1] == OP_UM_O_OTO:
            self.consome(OP_UM_O_OTO)
            self.parse_and()
            self.parse_restoXor()

    def parse_and(self):
        """ <and> -> <not> <restoAnd> ; """
        self.parse_not()
        self.parse_restoAnd()

    def parse_restoAnd(self):
        """ <restoAnd> -> 'tamem' <not> <restoAnd> | & ; """
        if self.token_atual()[1] == OP_TAMEM:
            self.consome(OP_TAMEM)
            self.parse_not()
            self.parse_restoAnd()

    def parse_not(self):
        """ <not> -> 'vam_marca' <not> | <rel> ; """
        if self.token_atual()[1] == OP_VAM_MARCA:
            self.consome(OP_VAM_MARCA)
            self.parse_not()
        else:
            self.parse_rel()

    def parse_rel(self):
        """ <rel> -> <add> <restoRel> ; """
        self.parse_add()
        self.parse_restoRel()

    def parse_restoRel(self):
        """ <restoRel> -> 'mema_coisa' <add> | 'neh_nada' <add> | '<' <add> | '<=' <add> | '>' <add> | '>=' <add> | & ; """
        atual = self.token_atual()[1]
        operadores_relacionais = {
            OP_MEMA_COISA: "'mema_coisa'",
            OP_NEH_NADA: "'neh_nada'",
            OP_MENOR: "'<'",
            OP_MENOR_IGUAL: "'<='",
            OP_MAIOR: "'>'",
            OP_MAIOR_IGUAL: "'>='"
        }
        
        if atual in operadores_relacionais:
            self.consome(atual)
            self.parse_add()
        else:
            return

    def parse_add(self):
        """ <add> -> <mult> <restoAdd> ; """
        self.parse_mult()
        self.parse_restoAdd()

    def parse_restoAdd(self):
        """ <restoAdd> -> '+' <mult> <restoAdd> | '-' <mult> <restoAdd> | & ; """
        atual = self.token_atual()[1]
        if atual in [OP_MAIS, OP_MENOS]:
            nome_esperado = "'+'" if atual == OP_MAIS else "'-'"
            self.consome(atual)
            self.parse_mult()
            self.parse_restoAdd()
        else:
            return

    def parse_mult(self):
        """ <mult> -> <uno> <restoMult> ; """
        self.parse_uno()
        self.parse_restoMult()

    def parse_restoMult(self):
        """ <restoMult> -> 'veiz' <uno> <restoMult> | 'sob' <uno> <restoMult> | '/' <uno> <restoMult> | '%' <uno> <restoMult> | & ; """
        atual = self.token_atual()[1]

        operadores_mult = {
            OP_VEIZ: "'veiz'",
            OP_SOB: "'sob'",
            OP_DIVISAO_INT: "'/'",
            OP_MODULO: "'%'"
        }
        
        if atual in operadores_mult:
            self.consome(atual)
            self.parse_uno()
            self.parse_restoMult()
        else:
            return

    def parse_uno(self):
        """ <uno> -> '+' <uno> | '-' <uno> | <fatorZao> ; """
        atual = self.token_atual()[1]
        if atual in [OP_MAIS, OP_MENOS]:
            nome_esperado = "'+'" if atual == OP_MAIS else "'-'"
            self.consome(atual)
            self.parse_uno()
        else:
            self.parse_fatorZao()

    def parse_fatorZao(self):
        """ <fatorZao> -> <fatorZin> | '(' <atrib> ')' ; """
        atual = self.token_atual()[1]
        if atual == DEL_ABRE_PAR:
            self.consome(DEL_ABRE_PAR)
            self.parse_atrib()
            self.consome(DEL_FECHA_PAR)
        else:
            self.parse_fatorZin()

    def iniciar(self):
        if self.tamanho == 0:
            print("Nenhum token para analisar.")
            return

        self.parse_function()

        if self.pos < self.tamanho:
            self.disparar_erro_sintatico("Fim do arquivo (Nenhum código fora da main)", self.token_atual())

        return True