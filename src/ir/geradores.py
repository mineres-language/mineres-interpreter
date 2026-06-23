"""Geradores de nomes únicos para temporárias (@_t1, @_t2, ...) e labels (L1, L2, ...)."""


class GeradorTemp:
    """Gera variáveis temporárias para resultados intermediários de expressões."""

    def __init__(self):
        self.contador = 0

    def proximo(self) -> str:
        """Retorna o próximo nome de temporária disponível."""
        self.contador += 1
        return f"@_t{self.contador}"

    def reset(self):
        """Reinicia o contador. Útil para testes."""
        self.contador = 0


class GeradorLabel:
    """Gera labels para pontos de salto (if/else, loops, etc.)."""

    def __init__(self):
        self.contador = 0

    def proximo(self) -> str:
        """Retorna o próximo nome de label disponível."""
        self.contador += 1
        return f"L{self.contador}"

    def reset(self):
        """Reinicia o contador. Útil para testes."""
        self.contador = 0
