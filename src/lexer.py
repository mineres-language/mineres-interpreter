from tokens import *

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

    def atual(self) -> str:
        """Retorna o caractere na posição atual sem avançar."""
        if self.pos >= self.tamanho:
            return '\0'
        return self.fonte[self.pos]

    def proximo(self) -> str:
        """Retorna o próximo caractere sem avançar."""
        if self.pos + 1 >= self.tamanho:
            return '\0'
        return self.fonte[self.pos + 1]

    def avanca(self):
        """Avança a posição e atualiza linha/coluna."""
        if self.pos < self.tamanho:
            if self.fonte[self.pos] == '\n':
                self.linha  += 1
                self.coluna  = 1
            else:
                self.coluna += 1
            self.pos += 1

    def peek(self, offset: int) -> str:
        """Retorna o caractere em pos + offset sem avançar."""
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
        return c in '0123456789ABCDEF'

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
        """Consome -- até o fim da linha."""
        self.avanca()  # -
        self.avanca()  # -
        while self.pos < self.tamanho and self.atual() != '\n':
            self.avanca()

    def pula_comentario_bloco(self, lin: int, col: int) -> bool:
        """
        Consome 'causo ... fim do causo'.
        Retorna True se fechou corretamente, False se chegou ao EOF sem fechar.
        """
        # consome 'causo'
        for _ in range(5):
            self.avanca()

        while self.pos < self.tamanho:
            # procura 'fim do causo'
            if self.fonte[self.pos:self.pos + 11] == 'fim do causo':
                for _ in range(11):
                    self.avanca()
                return True
            self.avanca()

        return False  # EOF sem fechar

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

        # Hexadecimal: 0x[0-9A-F]+
        if self.atual() == '0' and self.proximo() == 'x':
            self.avanca()  # 0
            self.avanca()  # x
            if not self.eh_digito_hex(self.atual()):
                # consome o lixo e retorna erro
                while self.pos < self.tamanho and not self.atual().isspace():
                    self.avanca()
                return (self.fonte[inicio:self.pos], ERRO_NUMERO, lin, col)
            while self.pos < self.tamanho and self.eh_digito_hex(self.atual()):
                self.avanca()
            return (self.fonte[inicio:self.pos], LIT_NUM_HEX, lin, col)

        # Octal: 0[1-7][0-7]*
        if self.atual() == '0' and self.eh_digito_oct(self.proximo()) and self.proximo() != '0':
            self.avanca()  # 0
            while self.pos < self.tamanho and self.eh_digito_oct(self.atual()):
                self.avanca()
            # se vier 8 ou 9: número mal formado
            if self.pos < self.tamanho and self.eh_digito(self.atual()):
                while self.pos < self.tamanho and self.eh_digito(self.atual()):
                    self.avanca()
                return (self.fonte[inicio:self.pos], ERRO_NUMERO, lin, col)
            return (self.fonte[inicio:self.pos], LIT_NUM_OCT, lin, col)

        # Inteiro ou float
        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        if self.pos < self.tamanho and self.atual() == '.':
            # float: [0-9]+.[0-9]*
            self.avanca()  # consome o ponto
            while self.pos < self.tamanho and self.eh_digito(self.atual()):
                self.avanca()
            return (self.fonte[inicio:self.pos], LIT_NUM_FLOAT, lin, col)

        return (self.fonte[inicio:self.pos], LIT_NUM_INT, lin, col)

    def le_float_por_ponto(self):
        """Lê float que começa com ponto: .[0-9]+"""
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        self.avanca()  # consome o ponto

        if not self.eh_digito(self.atual()):
            return (self.fonte[inicio:self.pos], ERRO_SIMBOLO, lin, col)

        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        return (self.fonte[inicio:self.pos], LIT_NUM_FLOAT, lin, col)

    def le_string(self):
        """Lê string delimitada por aspas duplas."""
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        self.avanca()  # abre "

        while self.pos < self.tamanho:
            c = self.atual()
            if c == '"':
                self.avanca()  # fecha "
                return (self.fonte[inicio:self.pos], LIT_STRING, lin, col)
            if c == '\n':
                return (self.fonte[inicio:self.pos], ERRO_STRING, lin, col)
            self.avanca()

        return (self.fonte[inicio:self.pos], ERRO_STRING, lin, col)

    def le_char(self):
        """Lê literal char no formato .'X'."""
        inicio = self.pos
        lin    = self.linha
        col    = self.coluna

        self.avanca()  # .
        self.avanca()  # o caractere

        if self.atual() == '.':
            self.avanca()  # .
            return (self.fonte[inicio:self.pos], LIT_CHAR, lin, col)

        return (self.fonte[inicio:self.pos], ERRO_SIMBOLO, lin, col)

    # -------------------------------------------------------------------------
    # Loop principal
    # -------------------------------------------------------------------------

    def tokenizar(self) -> bool:
        """
        Percorre o código-fonte e preenche self.tokens.
        Retorna True se terminou sem erros, False se encontrou erro léxico.
        """
        while self.pos < self.tamanho:
            self.pula_espacos()
            if self.pos >= self.tamanho:
                break

            lin = self.linha
            col = self.coluna
            c   = self.atual()

            # Comentário de linha e Divisão Inteira (/)
            if c == '/':
                if self.proximo() == '/':
                    self.pula_comentario_linha()
                    continue
                else:
                    self.avanca()
                    self.tokens.append(("/", OP_DIVISAO_INT, lin, col))
                    continue

            # Comentário de bloco: causo ... fim do causo
            if (c == 'c' and
                self.fonte[self.pos:self.pos + 5] == 'causo' and
                (self.pos + 5 >= self.tamanho or not self.eh_corpo_ident(self.peek(5)))):
                ok = self.pula_comentario_bloco(lin, col)
                if not ok:
                    self.erro = (f"Erro léxico: comentário 'causo' não fechado", lin, col)
                    self.tokens.append(("causo", ERRO_CAUSO, lin, col))
                    return False
                continue

            # Identificador ou palavra reservada
            if self.eh_letra(c) or c == '_':
                token = self.le_identificador_ou_reservada()
                self.tokens.append(token)
                continue

            # Número
            if self.eh_digito(c):
                token = self.le_numero()
                if token[1] in (ERRO_NUMERO,):
                    self.erro = (f"Erro léxico: número mal formado '{token[0]}'", lin, col)
                    self.tokens.append(token)
                    return False
                self.tokens.append(token)
                continue

            # Lógica do Ponto (Float, Char ou Ponto Final)
            if c == '.':
                # Float: .92
                if self.eh_digito(self.proximo()):
                    token = self.le_float_por_ponto()
                    if token[1] == ERRO_SIMBOLO:
                        self.erro = (f"Erro léxico: float mal formado", lin, col)
                        self.tokens.append(token)
                        return False
                    self.tokens.append(token)
                    continue
                # Char: .A. (Verifica se duas casas para frente tem outro ponto)
                elif self.peek(2) == '.':
                    token = self.le_char()
                    if token[1] == ERRO_SIMBOLO:
                        self.erro = (f"Erro léxico: char mal formado '{token[0]}'", lin, col)
                        self.tokens.append(token)
                        return False
                    self.tokens.append(token)
                    continue
                # Ponto Final Simples
                else:
                    self.avanca()
                    self.tokens.append((".", DEL_PONTO, lin, col))
                    continue

            # Char: .'X'.
            if c == '.' and self.proximo() == "'":
                token = self.le_char()
                if token[1] == ERRO_SIMBOLO:
                    self.erro = (f"Erro léxico: char mal formado '{token[0]}'", lin, col)
                    self.tokens.append(token)
                    return False
                self.tokens.append(token)
                continue

            # String
            if c == '"':
                token = self.le_string()
                if token[1] == ERRO_STRING:
                    self.erro = (f"Erro léxico: string não fechada '{token[0]}'", lin, col)
                    self.tokens.append(token)
                    return False
                self.tokens.append(token)
                continue

            # Operadores e delimitadores de um ou dois caracteres
            if c == '<':
                self.avanca()
                if self.atual() == '=':
                    self.avanca()
                    self.tokens.append(("<=", OP_MENOR_IGUAL, lin, col))
                else:
                    self.tokens.append(("<", OP_MENOR, lin, col))
                continue

            if c == '>':
                self.avanca()
                if self.atual() == '=':
                    self.avanca()
                    self.tokens.append((">=", OP_MAIOR_IGUAL, lin, col))
                else:
                    self.tokens.append((">", OP_MAIOR, lin, col))
                continue

            if c == '+':
                self.avanca()
                self.tokens.append(("+", OP_MAIS, lin, col))
                continue

            if c == '-':
                self.avanca()
                self.tokens.append(("-", OP_MENOS, lin, col))
                continue

            if c == '%':
                self.avanca()
                self.tokens.append(("%", OP_MODULO, lin, col))
                continue

            if c == '(':
                self.avanca()
                self.tokens.append(("(", DEL_ABRE_PAR, lin, col))
                continue

            if c == ')':
                self.avanca()
                self.tokens.append((")", DEL_FECHA_PAR, lin, col))
                continue

            if c == ',':
                self.avanca()
                self.tokens.append((",", DEL_VIRGULA, lin, col))
                continue

            if c == '{':
                self.avanca()
                self.tokens.append(("{", DEL_ABRE_CHAVE, lin, col))
                continue

            if c == '}':
                self.avanca()
                self.tokens.append(("}", DEL_FECHA_CHAVE, lin, col))
                continue

            # Símbolo desconhecido
            self.avanca()
            self.erro = (f"Erro léxico: símbolo desconhecido '{c}'", lin, col)
            self.tokens.append((c, ERRO_SIMBOLO, lin, col))
            return False

        return True