import sys
from lexer.tokens import *
from ir import GeradorTemp, GeradorLabel, TabelaSimbolos, NOME_DO_TIPO

PRIMEIROS_DE_STMT = {
    PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO,
    PR_XOVE, PR_OIA_PROCE_VE, 
    PR_UAI_SE, PR_ENQUANTO, PR_RODA_ESSE_TREM, PR_DEPENDENU,
    DEL_SIMBORA, PR_PARA_O_TREM, PR_TOCA_O_TREM, DEL_UAI,
    IDENTIFICADOR, LIT_NUM_INT, LIT_NUM_HEX, LIT_NUM_OCT,
    LIT_NUM_FLOAT, LIT_STRING, LIT_CHAR, PR_EH, PR_NUM_EH,
}

OP_PARA_IR = {
    OP_MAIS:         "add",
    OP_MENOS:        "sub",
    OP_VEIZ:         "mult",
    OP_SOB:          "div",
    OP_DIVISAO_INT:  "divI",
    OP_MODULO:       "mod",
    OP_TAMEM:        "and",
    OP_QUARQUE_UM:   "or",
    OP_UM_O_OTO:     "xor",
    OP_VAM_MARCA:    "not",
    OP_MENOR:        "less",
    OP_MENOR_IGUAL:  "leq",
    OP_MAIOR:        "gret",
    OP_MAIOR_IGUAL:  "geq",
    OP_MEMA_COISA:   "eq",
    OP_NEH_NADA:     "dif",
}


class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = 0 
        self.tamanho = len(tokens)

        self.gerador_temp  = GeradorTemp()
        self.gerador_label = GeradorLabel()
        self.tabela        = TabelaSimbolos()

        self.pilha_loops = []

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
            lexema = atual[0]
            self.avanca()
            return lexema
        else:
            # busca no dicionário reverso, se não achar, usa um genérico
            esperado = NOMES_TOKENS.get(codigo_esperado, f"Token {codigo_esperado}")
            self.disparar_erro_sintatico(esperado, atual)

    # -------------------------------------------------------------------------
    # Regras da Gramática (Árvore de Decisão)
    # -------------------------------------------------------------------------

    def parse_function(self) -> list:
        """ <function*> -> 'bora_cumpade' 'main' '(' ')' <bloco> ; """
        self.consome(PR_BORA_CUMPADE)
        self.consome(PR_MAIN)
        self.consome(DEL_ABRE_PAR)
        self.consome(DEL_FECHA_PAR)
        return self.parse_bloco()

    def parse_bloco(self) -> list:
        """ <bloco> -> 'simbora' <stmtList> 'cabo' ; """
        self.consome(DEL_SIMBORA)
        codigo = self.parse_stmtList()
        self.consome(DEL_CABO)
        return codigo

    def parse_stmtList(self) -> list:
        """ <stmtList> -> <stmt> <stmtList> | & ; """
        codigo = []
        atual = self.token_atual()[1]
        
        if atual in PRIMEIROS_DE_STMT:
            codigo.extend(self.parse_stmt())
            codigo.extend(self.parse_stmtList())
        elif atual == DEL_CABO:
            return codigo
        else:
            esperados = ("sintaxe de comando (ex: 'uai_se', 'enquanto_tiver_trem', "
                         "'trem_di_numeru', 'xove'...) ou fechamento 'cabo'")
            self.disparar_erro_sintatico(esperados, self.token_atual())

        return codigo

    def parse_stmt(self) -> list:
        atual = self.token_atual()[1]
        tipos_variaveis = {PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA, PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO} # Hash rápida O(1)
        
        if atual in tipos_variaveis:
            return self.parse_declaration()
        elif atual in {PR_XOVE, PR_OIA_PROCE_VE}:
            return self.parse_ioStmt()
        elif atual == PR_UAI_SE:
            return self.parse_ifStmt()
        elif atual == PR_ENQUANTO:
            return self.parse_whileStmt()
        elif atual == PR_RODA_ESSE_TREM:
            return self.parse_forStmt()
        elif atual == PR_DEPENDENU:
            return self.parse_caseStmt()
        elif atual == DEL_SIMBORA:
            return self.parse_bloco()
        elif atual == PR_PARA_O_TREM:
            tk = self.token_atual()
            self.consome(PR_PARA_O_TREM)
            self.consome(DEL_UAI)
            if not self.pilha_loops:
                print("\n[ERRO SEMÂNTICO]")
                print(f"Linha: {tk[2]}, Coluna: {tk[3]}")
                print("'para_o_trem' usado fora de um laço.")
                sys.exit(1)
            _, label_fim = self.pilha_loops[-1]
            return [("jump", label_fim, None, None)]
        elif atual == PR_TOCA_O_TREM:
            tk = self.token_atual()
            self.consome(PR_TOCA_O_TREM)
            self.consome(DEL_UAI)
            if not self.pilha_loops:
                print("\n[ERRO SEMÂNTICO]")
                print(f"Linha: {tk[2]}, Coluna: {tk[3]}")
                print("'toca_o_trem' usado fora de um laço.")
                sys.exit(1)
            label_inicio, _ = self.pilha_loops[-1]
            return [("jump", label_inicio, None, None)]

        elif atual in {DEL_UAI, DEL_PONTO_VIRGULA}:
            self.consome(DEL_UAI)
            return []  # statement vazio

        # caso padrão: expressão seguida de 'uai'
        codigo, _ = self.parse_atrib()
        self.consome(DEL_UAI)
        return codigo

    # -------------------------------------------------------------------------
    # Declaração de Variáveis
    # -------------------------------------------------------------------------

    def parse_declaration(self) -> list:
        """ <declaration> -> <type> <identList> 'uai' ; """
        tipo = self.parse_type()
        nomes = self.parse_identList()
        self.consome(DEL_UAI)

        codigo = []
        valor_inicial = self.tabela.valor_inicial(tipo)

        for nome, linha, coluna in nomes:
            self.tabela.declarar(nome, tipo, linha, coluna)
            codigo.append(("att", f"@{nome}", valor_inicial, None))

        return codigo

    def parse_type(self) -> int:
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
            return atual
        else:
            self.disparar_erro_sintatico("Tipo de variável", self.token_atual())

    def parse_identList(self) -> list:
        """ <identList> -> 'IDENT' <restoIdentList>
        Retorna lista de tuplas (nome, linha, coluna) dos identificadores.
        """
        tk = self.token_atual()
        nome = self.consome(IDENTIFICADOR)
        nomes = [(nome, tk[2], tk[3])]
        nomes.extend(self.parse_restoIdentList())
        return nomes

    def parse_restoIdentList(self) -> list:
        """ <restoIdentList> -> ',' 'IDENT' <restoIdentList> | & ; """
        nomes = []
        if self.token_atual()[1] == DEL_VIRGULA:
            self.consome(DEL_VIRGULA)
            tk = self.token_atual()
            nome = self.consome(IDENTIFICADOR)
            nomes.append((nome, tk[2], tk[3]))
            nomes.extend(self.parse_restoIdentList())
        return nomes

    # -------------------------------------------------------------------------
    # I/O (Prints e Inputs)
    # -------------------------------------------------------------------------

    def parse_ioStmt(self) -> list:
        """ <ioStmt> -> 'xove' '(' <type> ',' 'IDENT' ')' 'uai' | 'oia_proce_ve' '(' <outList> ')' 'uai' """
        atual = self.token_atual()[1]
        
        if atual == PR_XOVE: # Input
            self.consome(PR_XOVE)
            self.consome(DEL_ABRE_PAR)
            self.parse_type()
            self.consome(DEL_VIRGULA)
            tk = self.token_atual()
            nome = self.consome(IDENTIFICADOR)
            self.consome(DEL_FECHA_PAR)
            self.consome(DEL_UAI)
            self.tabela.verificar_uso(nome, tk[2], tk[3])
            return [("call", "read", f"@{nome}", None)]

        elif atual == PR_OIA_PROCE_VE:
            self.consome(PR_OIA_PROCE_VE)
            self.consome(DEL_ABRE_PAR)
            codigo = self.parse_outList()
            self.consome(DEL_FECHA_PAR)
            self.consome(DEL_UAI)
            return codigo

        self.disparar_erro_sintatico("'xove' ou 'oia_proce_ve'", self.token_atual())

    def parse_outList(self) -> list:
        """ <outList> -> <out> <restoOutList> """
        codigo = self.parse_out()
        codigo.extend(self.parse_restoOutList())
        return codigo

    def parse_out(self) -> list:
        """
        <out> -> <fatorZin>

        Gera tupla de print apropriada:
          - Se for variável: (call, print, var, null)
          - Se for literal:  (call, print, null, valor)
        """
        codigo, lugar, eh_variavel = self.parse_fatorZin_com_info()

        if eh_variavel:
            codigo.append(("call", "print", lugar, None))
        else:
            codigo.append(("call", "print", None, lugar))

        return codigo

    def parse_restoOutList(self) -> list:
        """ <restoOutList> -> ',' <out> <restoOutList> | & ; """
        codigo = []
        if self.token_atual()[1] == DEL_VIRGULA:
            self.consome(DEL_VIRGULA)
            codigo.extend(self.parse_out())
            codigo.extend(self.parse_restoOutList())
        return codigo

    # -------------------------------------------------------------------------
    # Estruturas de Controle
    # -------------------------------------------------------------------------

    def parse_ifStmt(self) -> list:
        """
        <ifStmt> -> 'uai_se' '(' <expr> ')' <stmt> <elsePart> ;

        Estrutura do IR gerado:
            ... código da condição ...
            (if, t_cond, L_then, L_else)
            (label, L_then, null, null)
            ... corpo do then ...
            (jump, L_fim, null, null)
            (label, L_else, null, null)
            ... corpo do else (vazio se não houver) ...
            (label, L_fim, null, null)
        """
        self.consome(PR_UAI_SE)
        self.consome(DEL_ABRE_PAR)
        cod_cond, lugar_cond = self.parse_expr()
        self.consome(DEL_FECHA_PAR)

        L_then = self.gerador_label.proximo()
        L_else = self.gerador_label.proximo()
        L_fim  = self.gerador_label.proximo()

        codigo = list(cod_cond)
        codigo.append(("if", lugar_cond, L_then, L_else))
        codigo.append(("label", L_then, None, None))
        codigo.extend(self.parse_stmt())
        codigo.append(("jump", L_fim, None, None))
        codigo.append(("label", L_else, None, None))
        codigo.extend(self.parse_elsePart())
        codigo.append(("label", L_fim, None, None))

        return codigo

    def parse_elsePart(self) -> list:
        """ <elsePart> -> 'uai_senao' <stmt> | & """
        if self.token_atual()[1] == PR_UAI_SENAO:
            self.consome(PR_UAI_SENAO)
            return self.parse_stmt()
        return []

    def parse_whileStmt(self) -> list:
        """
        <whileStmt> -> 'enquanto_tiver_trem' '(' <expr> ')' <stmt>

        Estrutura do IR gerado:
            (label, L_inicio, null, null)
            ... código da condição ...
            (if, t_cond, L_corpo, L_fim)
            (label, L_corpo, null, null)
            ... corpo ...
            (jump, L_inicio, null, null)
            (label, L_fim, null, null)
        """
        self.consome(PR_ENQUANTO)
        self.consome(DEL_ABRE_PAR)

        L_inicio = self.gerador_label.proximo()
        L_corpo  = self.gerador_label.proximo()
        L_fim    = self.gerador_label.proximo()

        codigo = [("label", L_inicio, None, None)]

        cod_cond, lugar_cond = self.parse_expr()
        codigo.extend(cod_cond)
        codigo.append(("if", lugar_cond, L_corpo, L_fim))

        self.consome(DEL_FECHA_PAR)

        codigo.append(("label", L_corpo, None, None))

        # entra num escopo de loop (para break/continue)
        self.pilha_loops.append((L_inicio, L_fim))
        codigo.extend(self.parse_stmt())
        self.pilha_loops.pop()

        codigo.append(("jump", L_inicio, None, None))
        codigo.append(("label", L_fim, None, None))

        return codigo

    def parse_forStmt(self) -> list:
        """
        <forStmt> -> 'roda_esse_trem' '(' <optExpr> ';' <optExpr> ';' <optExpr> ')' <stmt> ;

        Estrutura do IR gerado:
            ... código de inicialização ...
            (label, L_cond, null, null)
            ... código da condição ...
            (if, t_cond, L_corpo, L_fim)
            (label, L_corpo, null, null)
            ... corpo ...
            (label, L_incr, null, null)        <- continue salta para cá
            ... código do incremento ...
            (jump, L_cond, null, null)
            (label, L_fim, null, null)
        """
        self.consome(PR_RODA_ESSE_TREM)
        self.consome(DEL_ABRE_PAR)

        L_cond  = self.gerador_label.proximo()
        L_corpo = self.gerador_label.proximo()
        L_incr  = self.gerador_label.proximo()
        L_fim   = self.gerador_label.proximo()

        codigo = []

        # 1ª parte: inicialização
        cod_init, _ = self.parse_optExpr()
        codigo.extend(cod_init)
        self.consome(DEL_PONTO_VIRGULA)

        # 2ª parte: condição
        codigo.append(("label", L_cond, None, None))
        cod_cond, lugar_cond = self.parse_optExpr()
        codigo.extend(cod_cond)

        if lugar_cond is None:
            # condição vazia → loop infinito (sempre verdadeiro)
            codigo.append(("jump", L_corpo, None, None))
        else:
            codigo.append(("if", lugar_cond, L_corpo, L_fim))

        self.consome(DEL_PONTO_VIRGULA)

        # 3ª parte: incremento (gerado AGORA, mas inserido depois do corpo)
        cod_incr, _ = self.parse_optExpr()
        self.consome(DEL_FECHA_PAR)

        # corpo do for
        codigo.append(("label", L_corpo, None, None))

        # entra no escopo de loop. Continue deve saltar para o INCREMENTO,
        # então o "label de início" do loop, do ponto de vista de continue, é L_incr.
        self.pilha_loops.append((L_incr, L_fim))
        codigo.extend(self.parse_stmt())
        self.pilha_loops.pop()

        # incremento
        codigo.append(("label", L_incr, None, None))
        codigo.extend(cod_incr)
        codigo.append(("jump", L_cond, None, None))

        codigo.append(("label", L_fim, None, None))

        return codigo

    def parse_optExpr(self) -> tuple:
        """
        <optExpr> -> <atrib> | &
        Retorna (lista_codigo, lugar) ou ([], None) se vazio.
        """
        atual = self.token_atual()[1]
        if atual in {DEL_PONTO_VIRGULA, DEL_FECHA_PAR}:
            return [], None
        return self.parse_atrib()

    def parse_caseStmt(self) -> list:
        """
        <caseStmt> -> 'dependenu' '(' 'IDENT' ')' 'simbora' <dosCasos> 'cabo'

        Cada 'du_casu valor' vira um teste de igualdade que pula para
        seu corpo se igual, ou para o próximo teste se diferente.
        """
        self.consome(PR_DEPENDENU)
        self.consome(DEL_ABRE_PAR)
        tk = self.token_atual()
        var = self.consome(IDENTIFICADOR)
        self.consome(DEL_FECHA_PAR)
        self.consome(DEL_SIMBORA)

        self.tabela.verificar_uso(var, tk[2], tk[3])

        L_fim = self.gerador_label.proximo()

        # entra escopo de loop só pra suportar break dentro do dependenu.
        # (continue não faz sentido em switch — usuário deve evitar.)
        self.pilha_loops.append((L_fim, L_fim))

        var_ir = f"@{var}"
        codigo = self.parse_dosCasos(var_ir, L_fim)
        self.consome(DEL_CABO)

        self.pilha_loops.pop()

        codigo.append(("label", L_fim, None, None))
        return codigo

    def parse_dosCasos(self, var_switch: str, L_fim: str) -> list:
        """ <dosCasos> -> <doCaso> <restoDosCasos> """
        codigo = self.parse_doCaso(var_switch, L_fim)
        codigo.extend(self.parse_restoDosCasos(var_switch, L_fim))
        return codigo

    def parse_doCaso(self, var_switch: str, L_fim: str) -> list:
        """
        <doCaso> -> 'du_casu' <fatorZin> ':' <stmt>

        Gera:
            (eq, t_cmp, var_switch, valor_caso)
            (if, t_cmp, L_corpo, L_proximo)
            (label, L_corpo, null, null)
            ... corpo ...
            (jump, L_fim, null, null)
            (label, L_proximo, null, null)
        """
        self.consome(PR_DU_CASU)
        cod_valor, lugar_valor, _ = self.parse_fatorZin_com_info()
        self.consome(DEL_DOIS_PONTOS)

        t_cmp     = self.gerador_temp.proximo()
        L_corpo   = self.gerador_label.proximo()
        L_proximo = self.gerador_label.proximo()

        codigo = list(cod_valor)
        codigo.append(("eq", t_cmp, var_switch, lugar_valor))
        codigo.append(("if", t_cmp, L_corpo, L_proximo))
        codigo.append(("label", L_corpo, None, None))
        codigo.extend(self.parse_stmt())
        codigo.append(("jump", L_fim, None, None))
        codigo.append(("label", L_proximo, None, None))

        return codigo

    def parse_restoDosCasos(self, var_switch: str, L_fim: str) -> list:
        """
        <restoDosCasos> -> <doCaso><restoDosCasos>
                         | 'uai_so' ':' <stmt>
                         | &
        """
        atual = self.token_atual()[1]
        codigo = []

        if atual == PR_DU_CASU:
            codigo.extend(self.parse_doCaso(var_switch, L_fim))
            codigo.extend(self.parse_restoDosCasos(var_switch, L_fim))

        elif atual == PR_UAI_SO:
            self.consome(PR_UAI_SO)
            self.consome(DEL_DOIS_PONTOS)
            codigo.extend(self.parse_stmt())

        return codigo

    # -------------------------------------------------------------------------
    # Expressões Matemáticas e Lógicas
    # -------------------------------------------------------------------------

    def parse_expr(self) -> tuple:
        """ <expr> -> <atrib> ; """
        return self.parse_atrib()

    def parse_atrib(self) -> tuple:
        """
        <atrib> -> <or> <restoAtrib> ;

        Atribuição é tratada como expressão. Se for atribuição,
        gera (att, var, valor, null) e retorna a variável como lugar.
        """
        cod_esq, lugar_esq = self.parse_or()
        return self.parse_restoAtrib(cod_esq, lugar_esq)

    def parse_restoAtrib(self, cod_esq: list, lugar_esq: str) -> tuple:
        """
        <restoAtrib> -> 'fica_assim_entao' <atrib> | & ;

        Aqui validamos que o lado esquerdo da atribuição é uma variável
        declarada. Se for uma expressão complexa ou literal, é erro semântico.
        """
        if self.token_atual()[1] == OP_FICA_ASSIM_ENTAO:
            tk = self.token_atual()
            self.consome(OP_FICA_ASSIM_ENTAO)
            cod_dir, lugar_dir = self.parse_atrib()

            # validação: lado esquerdo deve ser variável declarada
            if cod_esq or not self._eh_identificador_simples(lugar_esq):
                print("\n[ERRO SEMÂNTICO]")
                print(f"Linha: {tk[2]}, Coluna: {tk[3]}")
                print("Lado esquerdo da atribuição deve ser um identificador simples.")
                sys.exit(1)

            # Limpa o '@' para verificar na tabela original
            nome_real = lugar_esq[1:] if lugar_esq.startswith('@') else lugar_esq
            self.tabela.verificar_uso(nome_real, tk[2], tk[3])

            codigo = list(cod_dir)
            codigo.append(("att", lugar_esq, lugar_dir, None))
            return codigo, lugar_esq

        return cod_esq, lugar_esq

    def _eh_identificador_simples(self, lugar: str) -> bool:
        """
        Retorna True se 'lugar' é um identificador válido (não temporária,
        não literal). Identificadores começam com letra ou underscore.
        Temporárias começam com 't' seguido de dígitos — mas isso colide
        com identificadores começando com 't', então usamos a tabela:
        é identificador simples se a string ESTIVER na tabela de símbolos.
        """
        if isinstance(lugar, str) and lugar.startswith('@'):
            nome_real = lugar[1:]
            return self.tabela.existe(nome_real)
        return False

    # ---- Expressões binárias com associatividade à esquerda ----

    def parse_or(self) -> tuple:
        """ <or> -> <xor> <restoOr> """
        cod, lugar = self.parse_xor()
        return self.parse_restoOr(cod, lugar)

    def parse_restoOr(self, cod_esq: list, lugar_esq: str) -> tuple:
        """ <restoOr> -> 'quarque_um' <xor> <restoOr> | & """
        if self.token_atual()[1] == OP_QUARQUE_UM:
            self.consome(OP_QUARQUE_UM)
            cod_dir, lugar_dir = self.parse_xor()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append(("or", t, lugar_esq, lugar_dir))
            return self.parse_restoOr(codigo, t)
        return cod_esq, lugar_esq

    def parse_xor(self) -> tuple:
        """ <xor> -> <and> <restoXor> """
        cod, lugar = self.parse_and()
        return self.parse_restoXor(cod, lugar)

    def parse_restoXor(self, cod_esq: list, lugar_esq: str) -> tuple:
        """ <restoXor> -> 'um_o_oto' <and> <restoXor> | & """
        if self.token_atual()[1] == OP_UM_O_OTO:
            self.consome(OP_UM_O_OTO)
            cod_dir, lugar_dir = self.parse_and()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append(("xor", t, lugar_esq, lugar_dir))
            return self.parse_restoXor(codigo, t)
        return cod_esq, lugar_esq

    def parse_and(self) -> tuple:
        """ <and> -> <not> <restoAnd> """
        cod, lugar = self.parse_not()
        return self.parse_restoAnd(cod, lugar)

    def parse_restoAnd(self, cod_esq: list, lugar_esq: str) -> tuple:
        """ <restoAnd> -> 'tamem' <not> <restoAnd> | & """
        if self.token_atual()[1] == OP_TAMEM:
            self.consome(OP_TAMEM)
            cod_dir, lugar_dir = self.parse_not()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append(("and", t, lugar_esq, lugar_dir))
            return self.parse_restoAnd(codigo, t)
        return cod_esq, lugar_esq

    def parse_not(self) -> tuple:
        """ <not> -> 'vam_marca' <not> | <rel> """
        if self.token_atual()[1] == OP_VAM_MARCA:
            self.consome(OP_VAM_MARCA)
            cod, lugar = self.parse_not()
            t = self.gerador_temp.proximo()
            codigo = list(cod)
            codigo.append(("not", t, lugar, None))
            return codigo, t
        return self.parse_rel()

    def parse_rel(self) -> tuple:
        """ <rel> -> <add> <restoRel> """
        cod, lugar = self.parse_add()
        return self.parse_restoRel(cod, lugar)

    def parse_restoRel(self, cod_esq: list, lugar_esq: str) -> tuple:
        """
        <restoRel> -> ('mema_coisa'|'neh_nada'|'<'|'<='|'>'|'>=') <add> | &

        Note: relacionais NÃO se encadeiam (a < b < c não é válido em C-like).
        Por isso não há recursão aqui.
        """
        atual = self.token_atual()[1]
        ops_rel = {OP_MEMA_COISA, OP_NEH_NADA, OP_MENOR, OP_MENOR_IGUAL,
                   OP_MAIOR, OP_MAIOR_IGUAL}

        if atual in ops_rel:
            op = OP_PARA_IR[atual]
            self.consome(atual)
            cod_dir, lugar_dir = self.parse_add()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append((op, t, lugar_esq, lugar_dir))
            return codigo, t

        return cod_esq, lugar_esq

    def parse_add(self) -> tuple:
        """ <add> -> <mult> <restoAdd> """
        cod, lugar = self.parse_mult()
        return self.parse_restoAdd(cod, lugar)

    def parse_restoAdd(self, cod_esq: list, lugar_esq: str) -> tuple:
        """ <restoAdd> -> ('+'|'-') <mult> <restoAdd> | & """
        atual = self.token_atual()[1]
        if atual in {OP_MAIS, OP_MENOS}:
            op = OP_PARA_IR[atual]
            self.consome(atual)
            cod_dir, lugar_dir = self.parse_mult()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append((op, t, lugar_esq, lugar_dir))
            return self.parse_restoAdd(codigo, t)
        return cod_esq, lugar_esq

    def parse_mult(self) -> tuple:
        """ <mult> -> <uno> <restoMult> """
        cod, lugar = self.parse_uno()
        return self.parse_restoMult(cod, lugar)

    def parse_restoMult(self, cod_esq: list, lugar_esq: str) -> tuple:
        """ <restoMult> -> ('veiz'|'sob'|'/'|'%') <uno> <restoMult> | & """
        atual = self.token_atual()[1]
        if atual in {OP_VEIZ, OP_SOB, OP_DIVISAO_INT, OP_MODULO}:
            op = OP_PARA_IR[atual]
            self.consome(atual)
            cod_dir, lugar_dir = self.parse_uno()
            t = self.gerador_temp.proximo()
            codigo = list(cod_esq) + list(cod_dir)
            codigo.append((op, t, lugar_esq, lugar_dir))
            return self.parse_restoMult(codigo, t)
        return cod_esq, lugar_esq

    def parse_uno(self) -> tuple:
        """
        <uno> -> '+' <uno> | '-' <uno> | <fatorZao>

        Operadores unários geram tupla no formato:
            (uno, "+", res, op)   ou   (uno, "-", res, op)
        """
        atual = self.token_atual()[1]
        if atual in {OP_MAIS, OP_MENOS}:
            sinal = "+" if atual == OP_MAIS else "-"
            self.consome(atual)
            cod, lugar = self.parse_uno()
            t = self.gerador_temp.proximo()
            codigo = list(cod)
            codigo.append(("uno", sinal, t, lugar))
            return codigo, t

        return self.parse_fatorZao()

    def parse_fatorZao(self) -> tuple:
        """ <fatorZao> -> <fatorZin> | '(' <atrib> ')' """
        if self.token_atual()[1] == DEL_ABRE_PAR:
            self.consome(DEL_ABRE_PAR)
            resultado = self.parse_atrib()
            self.consome(DEL_FECHA_PAR)
            return resultado

        cod, lugar, _ = self.parse_fatorZin_com_info()
        return cod, lugar

    def parse_fatorZin(self) -> tuple:
        """
        <fatorZin> -> 'STR' | 'IDENT' | 'NUMint' | ... | 'valorBooleano' | 'valorChar'

        Retorna (lista_codigo, lugar).
        """
        cod, lugar, _ = self.parse_fatorZin_com_info()
        return cod, lugar

    def parse_fatorZin_com_info(self) -> tuple:
        """
        Versão estendida que também retorna se o resultado é uma variável.

        Retorno: (lista_codigo, lugar, eh_variavel)
            eh_variavel é True se for um IDENTIFICADOR (variável do programa)
            e False se for um literal (string, número, char, booleano).
        """
        tk = self.token_atual()
        codigo_token, codigo, linha, coluna = tk[0], tk[1], tk[2], tk[3]

        literais_validos = {LIT_STRING, LIT_NUM_INT, LIT_NUM_HEX, LIT_NUM_OCT,
                            LIT_NUM_FLOAT, LIT_CHAR, PR_EH, PR_NUM_EH}

        if codigo == IDENTIFICADOR:
            self.consome(IDENTIFICADOR)
            self.tabela.verificar_uso(codigo_token, linha, coluna)
            return [], f"@{codigo_token}", True

        if codigo in literais_validos:
            self.consome(codigo)

            # Formata o lugar conforme o tipo
            if codigo == LIT_STRING:
                lugar = codigo_token  # strings são guardadas com aspas pelo formatador
            elif codigo == LIT_CHAR:
                lugar = codigo_token
            elif codigo == LIT_NUM_INT:
                lugar = int(codigo_token)
            elif codigo == LIT_NUM_HEX:
                lugar = int(codigo_token, 16)
            elif codigo == LIT_NUM_OCT:
                lugar = int(codigo_token, 8)
            elif codigo == LIT_NUM_FLOAT:
                lugar = float(codigo_token)
            elif codigo in {PR_EH, PR_NUM_EH}:
                lugar = codigo_token  # "eh" ou "num_eh"
            else:
                lugar = codigo_token

            return [], lugar, False

        self.disparar_erro_sintatico("Valor literal ou variável", tk)

    # =========================================================================
    # PONTO DE ENTRADA EXTERNO
    # =========================================================================

    def iniciar(self) -> list:
        """
        Inicia o parsing e retorna a lista de tuplas do código intermediário.
        Retorna lista vazia se não houver tokens.
        """
        if self.tamanho == 0:
            print("Nenhum token para analisar.")
            return []
        
        codigo = self.parse_function()

        if self.pos < self.tamanho:
            self.disparar_erro_sintatico(
                "Fim do arquivo (Nenhum código fora da main)",
                self.token_atual()
            )

        return codigo
