from tokens import *
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
        """Interrompe a execução imediatamente e exibe o erro fatal simulando o formato de saída."""
        print(f"\n[ERRO FATAL LÉXICO]")
        print(f'("{lexema}", "{tipo_erro}", {lin}, {col})')
        print("Execução abortada. Nenhum arquivo de saída foi gerado.\n")
        
        sys.exit(1)

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
        """Consome -- até o fim da linha."""
        self.avanca()  # -
        self.avanca()  # -
        while self.pos < self.tamanho and self.atual() != '\n':
            self.avanca()

    def pula_comentario_bloco(self, lin: int, col: int) -> bool:
        """
        Consome 'causo ... fim_do_causo'.
        Retorna True se fechou corretamente, False se chegou ao EOF sem fechar.
        """
        # consome 'causo'
        for _ in range(5):
            self.avanca()

        while self.pos < self.tamanho:
            # procura 'fim_do_causo'
            if self.fonte[self.pos:self.pos + 12] == 'fim_do_causo':
                for _ in range(12):
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
            # Se logo depois do 0x vier lixo (Ex: 0xZ)
            if not self.eh_digito_hex(self.atual()):
                while self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                    self.avanca()
                self.disparar_erro_fatal("Número hexadecimal mal formado", self.fonte[inicio:self.pos], lin, col)
            # Consome os hexadecimais válidos (No 0x3G, ele para no 3)
            while self.pos < self.tamanho and self.eh_digito_hex(self.atual()):
                self.avanca()
            # Verifica se sobrou lixo colado no final (O 'G' do 0x3G cai aqui!)
            if self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                while self.pos < self.tamanho and self.eh_corpo_ident(self.atual()):
                    self.avanca()
                self.disparar_erro_fatal("Número hexadecimal mal formado", self.fonte[inicio:self.pos], lin, col)
                
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
                self.disparar_erro_fatal("Número octal mal formado", self.fonte[inicio:self.pos], lin, col)
            return (self.fonte[inicio:self.pos], LIT_NUM_OCT, lin, col)

        # Inteiro ou float
        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        if self.pos < self.tamanho and self.atual() == '.':
            # float: [0-9]+.[0-9]*
            # Encontrou um ponto depois de dígitos (ex: 10.)
            inicio_erro = self.pos - len(self.fonte[inicio:self.pos]) # para pegar o número todo
            self.avanca()  # consome o ponto

            if not self.eh_digito(self.atual()):
            # Se depois do ponto não vier um número = erro!
                self.disparar_erro_fatal("Float mal formado (falta dígitos após o ponto)", self.fonte[inicio:self.pos], lin, col)

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
            self.disparar_erro_fatal("Float mal formado", self.fonte[inicio:self.pos], lin, col)

        while self.pos < self.tamanho and self.eh_digito(self.atual()):
            self.avanca()

        return (self.fonte[inicio:self.pos], LIT_NUM_FLOAT, lin, col)

    def processa_escape(self, c: str) -> str:
        """Processa sequência de escape em strings."""
        if c == 'n':
            return '\n'
        elif c == 't':
            return '\t'
        elif c == '"':
            return '"'
        elif c == '\\':
            return '\\'
        else:
            return '\\' + c

    def decodifica_string(self, raw: str) -> str:
        """Decodifica escapes em uma string já extraída das aspas."""
        i = 0
        out = ''
        while i < len(raw):
            if raw[i] == '\\' and i + 1 < len(raw):
                i += 1
                out += self.processa_escape(raw[i])
            else:
                out += raw[i]
            i += 1
        return out

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
                raw = self.fonte[inicio+1:self.pos-1]
                return (self.decodifica_string(raw), LIT_STRING, lin, col)
            if c == '\n':
                self.disparar_erro_fatal("String não fechada", self.fonte[inicio:self.pos], lin, col)
            self.avanca()

        self.disparar_erro_fatal("String não fechada", self.fonte[inicio:self.pos], lin, col)
   
    def le_char(self):
        """Lê literal char delimitado por aspas simples ('X')."""
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
                    self.disparar_erro_fatal("Comentário multilinha não fechado", "causo", lin, col)
                continue

            # Identificador ou palavra reservada
            if self.eh_letra(c) or c == '_':
                token = self.le_identificador_ou_reservada()
                self.tokens.append(token)
                continue

            # Número
            if self.eh_digito(c):
                token = self.le_numero()
                self.tokens.append(token)
                continue

            # Lógica do Ponto (Float ou Ponto Final)
            if c == '.':
                if self.eh_digito(self.proximo()):
                    token = self.le_float_por_ponto()
                    self.tokens.append(token)
                    continue
                else:
                    self.disparar_erro_fatal("Float mal formado (ponto isolado)", ".", lin, col)

            # Char ('X')
            if c == "'":
                token = self.le_char()
                self.tokens.append(token)
                continue

            # String
            if c == '"':
                token = self.le_string()
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

            if c == ';':
                self.avanca()
                self.tokens.append((";", DEL_PONTO_VIRGULA, lin, col))
                continue
                
            if c == ':':
                self.avanca()
                self.tokens.append((": ", DEL_DOIS_PONTOS, lin, col))
                continue

            # Símbolo desconhecido
            self.avanca()
            self.disparar_erro_fatal("Símbolo desconhecido", c, lin, col)

        return True