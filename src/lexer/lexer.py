from .tokens import *
import sys

class Lexer:
    def __init__(self, fonte: str):
        self.fonte   = fonte
        self.tamanho = len(fonte)
        self.pos     = 0
        self.linha   = 1
        self.coluna  = 1
        self.tokens  = []
        self.erro    = None  # (mensagem, linha, coluna)

    # -------------------------------------------------------------------------
    # Helpers de navegação
    # -------------------------------------------------------------------------

    def disparar_erro_fatal(self, tipo_erro: str, lexema: str, lin: int, col: int):
        print(f"\n[ERRO FATAL LÉXICO]")
        print(f'("{lexema}", "{tipo_erro}", {lin}, {col})')
        print("Execução abortada. Lista de tokens não foi gerada.\n")
        
        sys.exit(1)

    def atual(self) -> str:
        if self.pos >= self.tamanho:
            return '\0'
        return self.fonte[self.pos]

    def proximo(self) -> str:
        if self.pos + 1 >= self.tamanho:
            return '\0'
        return self.fonte[self.pos + 1]

    def avanca(self):
        if self.pos < self.tamanho:
            if self.fonte[self.pos] == '\n':
                self.linha  += 1
                self.coluna  = 1
            else:
                self.coluna += 1
            self.pos += 1

    def peek(self, offset: int) -> str:
        idx = self.pos + offset
        if idx >= self.tamanho:
            return '\0'
        return self.fonte[idx]

    # -------------------------------------------------------------------------
    # Helpers de classificação
    # -------------------------------------------------------------------------

    def eh_letra(self, c: str) -> bool:
        return c.isalpha()

    def eh_digito(self, c: str) -> bool:
        return c.isdigit()

    def eh_digito_hex(self, c: str) -> bool:
        return c in '0123456789ABCDEFabcdef'

    def eh_digito_oct(self, c: str) -> bool:
        return c in '01234567'

    def eh_corpo_ident(self, c: str) -> bool:
        return c.isalnum() or c == '_'

    # -------------------------------------------------------------------------
    # Pular espaços e comentários
    # -------------------------------------------------------------------------

    def pula_espacos(self):
        while self.pos < self.tamanho and self.atual().isspace():
            self.avanca()

    def pula_comentario_linha(self):
        self.avanca()  # /
        self.avanca()  # /
        while self.pos < self.tamanho and self.atual() != '\n':
            self.avanca()

    def pula_comentario_bloco(self, lin: int, col: int) -> bool:
        # consome 'causo'
        for _ in range(5):
            self.avanca()

        # otimização: Delega a busca pesada para o C do interpretador Python
        pos_fim = self.fonte.find('fim_do_causo', self.pos)
        
        while pos_fim != -1:
            idx_after = pos_fim + 12
            # garante que não é um falso positivo colado em letras (ex: 'fim_do_causos')
            if idx_after >= self.tamanho or not self.eh_corpo_ident(self.fonte[idx_after]):
                # se achou, avança o ponteiro principal ('self.pos') de forma segura
                # para garantir que as linhas e colunas sejam atualizadas corretamente
                while self.pos < idx_after:
                    self.avanca()
                return True
            
            # se for falso positivo, continua a busca a partir da próxima letra
            pos_fim = self.fonte.find('fim_do_causo', pos_fim + 1)

        # se chegou aqui, não encontrou o fechamento. Avança tudo para engatilhar o EOF.
        while self.pos < self.tamanho:
            self.avanca()
            
        return False

    # -------------------------------------------------------------------------
    # Reconhecedores de token
    # -------------------------------------------------------------------------

    def le_identificador_ou_reservada(self):
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        while self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
            self.avanca()

        lexema = self.fonte[inicio:self.pos]
        codigo = PALAVRAS_RESERVADAS.get(lexema, IDENTIFICADOR)
        return (lexema, codigo, lin, col)

    def le_numero(self):
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        # hexadecimal: 0x[0-9A-F]+
        if self.atual() == '0' and self.proximo() == 'x':
            self.avanca()  # 0
            self.avanca()  # x
            # se logo depois do 0x vier lixo
            if not self.eh_digito_hex(self.atual()):
                while self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                    self.avanca()
                self.disparar_erro_fatal("Número hexadecimal mal formado", self.fonte[inicio:self.pos], lin, col)
            # consome os hexadecimais válidos (No 0x3G, ele para no 3)
            while self.pos < self.tamanho and self.eh_digito_hex(self.atual()):
                self.avanca()
            # verifica se sobrou lixo colado no final (O 'G' do 0x3G cai aqui!)
            if self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                while self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                    self.avanca()
                self.disparar_erro_fatal("Número hexadecimal mal formado", self.fonte[inicio:self.pos], lin, col)
                
            return (self.fonte[inicio:self.pos], LIT_NUM_HEX, lin, col)
        
        # octal: 0[1-7][0-7]*
        if self.atual() == '0' and self.eh_digito_oct(self.proximo()):
            self.avanca()  # 0
            while self.pos < self.tamanho and self.eh_digito_oct(self.atual()):
                self.avanca()
            # se vier 8 ou 9: número mal formado
            if self.pos < self.tamanho and self.eh_digito(self.atual()):
                while self.pos < self.tamanho and self.eh_digito(self.atual()):
                    self.avanca()
                self.disparar_erro_fatal("Número octal mal formado", self.fonte[inicio:self.pos], lin, col)
            return (self.fonte[inicio:self.pos], LIT_NUM_OCT, lin, col)

        # inteiro ou float
        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        if self.pos < self.tamanho and self.atual() == '.':
            # float: [0-9]+.[0-9]*
            self.avanca()  # consome o primeiro ponto

            if not self.eh_digito(self.atual()) and self.atual() != '.':
                lexema_formatado = self.fonte[inicio:self.pos] + '0'
                return(lexema_formatado, LIT_NUM_FLOAT, lin, col)

            # consome as casas decimais
            while self.pos < self.tamanho and self.eh_digito(self.atual()):
                self.avanca()
                
            # verifica se tem lixo como múltiplos pontos (ex: 12.12.12)
            if self.pos < self.tamanho and self.atual() == '.':
                while self.pos < self.tamanho and (self.eh_digito(self.atual()) or self.atual() == '.'):
                    self.avanca()
                self.disparar_erro_fatal("Número float mal formado (múltiplos pontos)", self.fonte[inicio:self.pos], lin, col)

            return (self.fonte[inicio:self.pos], LIT_NUM_FLOAT, lin, col)

        return (self.fonte[inicio:self.pos], LIT_NUM_INT, lin, col)
    
    def le_float_por_ponto(self):
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        self.avanca()  # consome o ponto

        # se for apenas o ponto isolado (ex: ". "), o loop principal já deve tratar ou disparar aqui
        if not self.eh_digito(self.atual()):
            self.disparar_erro_fatal("Float mal formado", self.fonte[inicio:self.pos], lin, col)

        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        # formata ".5" para "0.5"
        lexema_final = "0" + self.fonte[inicio:self.pos]
        return (lexema_final, LIT_NUM_FLOAT, lin, col)

    def processa_escape(self, c: str) -> str:
        if c == 'n':
            return '\n'
        elif c == 't':
            return '\t'
        elif c == '"':
            return '\"'
        elif c == "'":
            return "\'"
        elif c == '\\':
            return '\\'
        else:
            self.disparar_erro_fatal("Escape inválido", "\\" + c, self.linha, self.coluna)

    def le_string(self):
        inicio_pos = self.pos
        lin, col = self.linha, self.coluna
        self.avanca()  # Pula a aspa de abertura (")
        
        conteudo_processado = []

        while self.pos < self.tamanho:
            c = self.atual()

            if c == '\\':  # encontrou um escape
                self.avanca() # pula a barra
                if self.pos >= self.tamanho:
                    self.disparar_erro_fatal("Escape inválido no final da string", self.fonte[inicio_pos:self.pos], lin, col)
                proximo = self.atual()
                # chama sua função de processamento de escape
                conteudo_processado.append(self.processa_escape(proximo))
            elif c == '"':  # encontrou o fechamento real
                self.avanca()
                # retorna o conteúdo já montado/processado
                resultado = "".join(conteudo_processado)
                return (resultado, LIT_STRING, lin, col)
            elif c == '\n':
                self.disparar_erro_fatal("String não fechada antes da quebra de linha", self.fonte[inicio_pos:self.pos], lin, col)
            else:
                conteudo_processado.append(c)
            
            self.avanca()

        self.disparar_erro_fatal("String não fechada (EOF)", self.fonte[inicio_pos:self.pos], lin, col)

    def le_char(self):
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        self.avanca()  # consome a aspa simples de abertura '

        if self.pos >= self.tamanho:
            self.disparar_erro_fatal("Char mal formado", self.fonte[inicio:self.pos], lin, col)

        c = self.atual()

        if c == "'":
            # char vazio ou aspas consecutivas
            self.disparar_erro_fatal("Char mal formado", self.fonte[inicio:self.pos+1], lin, col)

        if c == "\\":
            # suporta escape em char '\n', '\'', '\\', etc.
            self.avanca()
            if self.pos >= self.tamanho:
                self.disparar_erro_fatal("Char mal formado", self.fonte[inicio:self.pos], lin, col)
            c = self.processa_escape(self.atual())
            self.avanca()
        else:
            self.avanca()

        # agora deve vir a aspa de fechamento
        if self.pos >= self.tamanho or self.atual() != "'":
            self.disparar_erro_fatal("Char mal formado", self.fonte[inicio:self.pos], lin, col)

        self.avanca()  # consome a aspa simples de fechamento '

        return (c, LIT_CHAR, lin, col)

    def tokenizar(self) -> bool:
        while self.pos < self.tamanho:
            self.pula_espacos()
            if self.pos >= self.tamanho:
                break

            lin = self.linha
            col = self.coluna
            c   = self.atual()

            # comentário de linha e Divisão Inteira (/)
            if c == '/':
                if self.proximo() == '/':
                    self.pula_comentario_linha()
                    continue
                else:
                    self.avanca()
                    self.tokens.append(("/", OP_DIVISAO_INT, lin, col))
                    continue

            # comentário de bloco: causo ... fim do causo
            if (c == 'c' and
                self.fonte[self.pos:self.pos + 5] == 'causo' and
                (self.pos + 5 >= self.tamanho or not self.eh_corpo_ident(self.peek(5)))):
                ok = self.pula_comentario_bloco(lin, col)
                if not ok:
                    self.disparar_erro_fatal("Comentário multilinha não fechado", "causo", lin, col)
                continue

            # identificador ou palavra reservada
            if self.eh_letra(c) or c == '_':
                token = self.le_identificador_ou_reservada()
                self.tokens.append(token)
                continue

            # número
            if self.eh_digito(c):
                token = self.le_numero()
                self.tokens.append(token)
                continue

            # lógica do ponto
            if c == '.':
                if self.eh_digito(self.proximo()):
                    token = self.le_float_por_ponto()
                    self.tokens.append(token)
                    continue
                else:
                    self.disparar_erro_fatal("Float mal formado (ponto isolado)", ".", lin, col)

            # char ('X')
            if c == "'":
                token = self.le_char()
                self.tokens.append(token)
                continue

            # string
            if c == '"':
                token = self.le_string()
                self.tokens.append(token)
                continue

            # operadores e delimitadores de um ou dois caracteres
            if c == '<':
                self.avanca()
                if self.atual() == '=':
                    self.avanca()
                    self.tokens.append(("<=", OP_MENOR_IGUAL, lin, col))
                else:
                    self.tokens.append(("<", OP_MENOR, lin, col))
            elif c == '>':
                self.avanca()
                if self.atual() == '=':
                    self.avanca()
                    self.tokens.append((">=", OP_MAIOR_IGUAL, lin, col))
                else:
                    self.tokens.append((">", OP_MAIOR, lin, col))
            elif c == '+':
                self.avanca()
                self.tokens.append(("+", OP_MAIS, lin, col))
            elif c == '-':
                self.avanca()
                self.tokens.append(("-", OP_MENOS, lin, col))
            elif c == '%':
                self.avanca()
                self.tokens.append(("%", OP_MODULO, lin, col))
            elif c == '(':
                self.avanca()
                self.tokens.append(("(", DEL_ABRE_PAR, lin, col))
            elif c == ')':
                self.avanca()
                self.tokens.append((")", DEL_FECHA_PAR, lin, col))
            elif c == ',':
                self.avanca()
                self.tokens.append((",", DEL_VIRGULA, lin, col))
            elif c == '{':
                self.avanca()
                self.tokens.append(("{", DEL_ABRE_CHAVE, lin, col))
            elif c == '}':
                self.avanca()
                self.tokens.append(("}", DEL_FECHA_CHAVE, lin, col))
            elif c == ';':
                self.avanca()
                self.tokens.append((";", DEL_PONTO_VIRGULA, lin, col))
            elif c == ':':
                self.avanca()
                self.tokens.append((":", DEL_DOIS_PONTOS, lin, col))
            else:
                self.avanca()
                self.disparar_erro_fatal("Símbolo desconhecido", c, lin, col)

        return True
    
def formata_tokens(tokens: list) -> str:
    linhas = ["[\n"]
    for i, (lexema, codigo, linha, coluna) in enumerate(tokens):
        lex_str = f'"{lexema}"'
        virgula = "," if i < len(tokens) - 1 else ""
        linhas.append(f"\t({lex_str:<20}, {codigo:>3}, {linha}, {coluna:>2}){virgula}\n")
    linhas.append("]")
    return "".join(linhas)