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
        
        # Agora o FIRST engloba blocos, controles, quebras, IO e variáveis
        primeiros_de_stmt = [
            PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO,
            PR_XOVE, PR_OIA_PROCE_VE, 
            PR_UAI_SE, PR_ENQUANTO, PR_RODA_ESSE_TREM, PR_DEPENDENU,
            DEL_SIMBORA, PR_PARA_O_TREM, PR_TOCA_O_TREM, DEL_UAI
        ]
        
        # Observação: <atrib> (expressões puras como 'x fica_assim_entao 5 uai') serão 
        # tratadas aqui na Etapa 4.
        
        if atual in primeiros_de_stmt or atual == IDENTIFICADOR or atual in [LIT_NUM_INT, LIT_NUM_FLOAT, LIT_STRING, LIT_CHAR]:
            self.parse_stmt()
            self.parse_stmtList()
        elif atual == DEL_CABO:
            return # Fim da lista de comandos
        else:
            self.disparar_erro_sintatico("Início de comando válido ou 'cabo'", self.token_atual())

    def parse_stmt(self):
        """ <stmt> -> <forStmt> | <ioStmt> | <whileStmt> | <atrib> 'uai' | <ifStmt> | <caseStmt> | <bloco> | ... """
        atual = self.token_atual()[1]
        tipos_variaveis = [PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO]
        
        if atual in tipos_variaveis:
            self.parse_declaration()
        elif atual in [PR_XOVE, PR_OIA_PROCE_VE]:
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
            self.consome(PR_PARA_O_TREM, "'para_o_trem'")
            self.consome(DEL_UAI, "'uai'")
        elif atual == PR_TOCA_O_TREM:
            self.consome(PR_TOCA_O_TREM, "'toca_o_trem'")
            self.consome(DEL_UAI, "'uai'")
        elif atual == DEL_UAI: # Comando vazio
            self.consome(DEL_UAI, "'uai'")
        else:
            # Temporário para a Etapa 4 (Expressões Isoladas)
            self.parse_atrib()
            self.consome(DEL_UAI, "'uai'")
    
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
    # Estruturas de Controle
    # -------------------------------------------------------------------------

    def parse_ifStmt(self):
        """ <ifStmt> -> 'uai_se' '(' <expr> ')' <stmt> <elsePart> ; """
        self.consome(PR_UAI_SE, "'uai_se'")
        self.consome(DEL_ABRE_PAR, "'('")
        self.parse_expr()
        self.consome(DEL_FECHA_PAR, "')'")
        self.parse_stmt()
        self.parse_elsePart()

    def parse_elsePart(self):
        """ <elsePart> -> 'uai_senao' <stmt> | & ; """
        if self.token_atual()[1] == PR_UAI_SENAO:
            self.consome(PR_UAI_SENAO, "'uai_senao'")
            self.parse_stmt()
        else:
            return # Vazio / Epsilon

    def parse_whileStmt(self):
        """ <whileStmt> -> 'enquanto_tiver_trem' '(' <expr> ')' <stmt> ; """
        self.consome(PR_ENQUANTO, "'enquanto_tiver_trem'")
        self.consome(DEL_ABRE_PAR, "'('")
        self.parse_expr()
        self.consome(DEL_FECHA_PAR, "')'")
        self.parse_stmt()

    def parse_forStmt(self):
        """ <forStmt> -> 'roda_esse_trem' '(' <optExpr> ';' <optExpr> ';' <optExpr> ')' <stmt> ; """
        self.consome(PR_RODA_ESSE_TREM, "'roda_esse_trem'")
        self.consome(DEL_ABRE_PAR, "'('")
        self.parse_optExpr()
        self.consome(DEL_PONTO_VIRGULA, "';'")
        self.parse_optExpr()
        self.consome(DEL_PONTO_VIRGULA, "';'")
        self.parse_optExpr()
        self.consome(DEL_FECHA_PAR, "')'")
        self.parse_stmt()

    def parse_optExpr(self):
        """ <optExpr> -> <atrib> | & ; """
        atual = self.token_atual()[1]
        # Se for um delimitador fechando ou separando, significa que a expressão é vazia
        if atual in [DEL_PONTO_VIRGULA, DEL_FECHA_PAR]:
            return
        else:
            self.parse_atrib()

    def parse_caseStmt(self):
        """ <caseStmt> -> 'dependenu' '(' 'IDENT' ')' 'simbora' <dosCasos> 'cabo' ; """
        self.consome(PR_DEPENDENU, "'dependenu'")
        self.consome(DEL_ABRE_PAR, "'('")
        self.consome(IDENTIFICADOR, "Identificador da variável")
        self.consome(DEL_FECHA_PAR, "')'")
        self.consome(DEL_SIMBORA, "'simbora'")
        self.parse_dosCasos()
        self.consome(DEL_CABO, "'cabo'")

    def parse_dosCasos(self):
        """ <dosCasos> -> <doCaso> <restoDosCasos> """
        self.parse_doCaso()
        self.parse_restoDosCasos()

    def parse_doCaso(self):
        """ <doCaso> -> 'du_casu' <fatorZin> ':' <stmt> """
        self.consome(PR_DU_CASU, "'du_casu'")
        self.parse_fatorZin()
        self.consome(DEL_DOIS_PONTOS, "':'")
        self.parse_stmt()

    def parse_restoDosCasos(self):
        """ <restoDosCasos> -> <doCaso><restoDosCasos> | 'default' ':' <stmt> | & """
        atual = self.token_atual()[1]
        
        if atual == PR_DU_CASU:
            self.parse_doCaso()
            self.parse_restoDosCasos()
            
        # Atenção: O professor usou a string 'default' na gramática. 
        # Como não criamos um PR_DEFAULT, vamos ler como um identificador com o texto "default"
        elif atual == IDENTIFICADOR and self.token_atual()[0] == "default":
            self.consome(IDENTIFICADOR, "'default'")
            self.consome(DEL_DOIS_PONTOS, "':'")
            self.parse_stmt()
        else:
            return # Vazio / Epsilon
            
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
            self.consome(OP_FICA_ASSIM_ENTAO, "'fica_assim_entao'")
            self.parse_atrib()

    def parse_or(self):
        """ <or> -> <xor> <restoOr> ; """
        self.parse_xor()
        self.parse_restoOr()

    def parse_restoOr(self):
        """ <restoOr> -> 'quarque_um' <xor> <restoOr> | & ; """
        if self.token_atual()[1] == OP_QUARQUE_UM:
            self.consome(OP_QUARQUE_UM, "'quarque_um'")
            self.parse_xor()
            self.parse_restoOr()

    def parse_xor(self):
        """ <xor> -> <and> <restoXor> ; """
        self.parse_and()
        self.parse_restoXor()

    def parse_restoXor(self):
        """ <restoXor> -> 'um_o_oto' <and> <restoXor> | & ; """
        if self.token_atual()[1] == OP_UM_O_OTO:
            self.consome(OP_UM_O_OTO, "'um_o_oto'")
            self.parse_and()
            self.parse_restoXor()

    def parse_and(self):
        """ <and> -> <not> <restoAnd> ; """
        self.parse_not()
        self.parse_restoAnd()

    def parse_restoAnd(self):
        """ <restoAnd> -> 'tamem' <not> <restoAnd> | & ; """
        if self.token_atual()[1] == OP_TAMEM:
            self.consome(OP_TAMEM, "'tamem'")
            self.parse_not()
            self.parse_restoAnd()

    def parse_not(self):
        """ <not> -> 'vam_marca' <not> | <rel> ; """
        if self.token_atual()[1] == OP_VAM_MARCA:
            self.consome(OP_VAM_MARCA, "'vam_marca'")
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
            self.consome(atual, operadores_relacionais[atual])
            self.parse_add()
            # Não tem recursão aqui porque não se encadeia a < b < c na mesma regra
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
            self.consome(atual, nome_esperado)
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
            self.consome(atual, operadores_mult[atual])
            self.parse_uno()
            self.parse_restoMult()
        else:
            return

    def parse_uno(self):
        """ <uno> -> '+' <uno> | '-' <uno> | <fatorZao> ; """
        atual = self.token_atual()[1]
        if atual in [OP_MAIS, OP_MENOS]:
            nome_esperado = "'+'" if atual == OP_MAIS else "'-'"
            self.consome(atual, nome_esperado)
            self.parse_uno()
        else:
            self.parse_fatorZao()

    def parse_fatorZao(self):
        """ <fatorZao> -> <fatorZin> | '(' <atrib> ')' ; """
        atual = self.token_atual()[1]
        if atual == DEL_ABRE_PAR:
            self.consome(DEL_ABRE_PAR, "'('")
            self.parse_atrib()
            self.consome(DEL_FECHA_PAR, "')'")
        else:
            self.parse_fatorZin()

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