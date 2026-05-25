"""
Geradores de nomes únicos para variáveis temporárias e labels.

Estes geradores são usados durante a geração de código intermediário
para criar identificadores que não conflitam com variáveis do programa.
"""


class GeradorTemp:
    """
    Gera nomes de variáveis temporárias no formato t1, t2, t3, ...

    Usado para armazenar resultados intermediários de expressões.
    Exemplo: a + b * c gera duas temporárias (uma pra b*c e outra pra a+t1).
    """

    def __init__(self):
        self.contador = 0

    def proximo(self) -> str:
        """Retorna o próximo nome de temporária disponível."""
        self.contador += 1
        return f"@t{self.contador}"

    def reset(self):
        """Reinicia o contador. Útil para testes."""
        self.contador = 0


class GeradorLabel:
    """
    Gera nomes de labels no formato L1, L2, L3, ...

    Usado para marcar pontos de salto no código intermediário
    (início de loops, ramos de if/else, fim de blocos, etc.).
    """

    def __init__(self):
        self.contador = 0

    def proximo(self) -> str:
        """Retorna o próximo nome de label disponível."""
        self.contador += 1
        return f"L{self.contador}"

    def reset(self):
        """Reinicia o contador. Útil para testes."""
        self.contador = 0
