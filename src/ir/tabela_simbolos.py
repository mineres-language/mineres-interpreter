"""
Tabela de Símbolos.

Mantém o registro de todas as variáveis declaradas no programa,
seus tipos, e fornece a base para análise semântica:
    - Detecção de variável não declarada
    - Detecção de redeclaração
    - Inferência de valor inicial padrão por tipo

Como o Minerês só tem a função 'main' (sem funções aninhadas),
usamos uma tabela única e plana, sem aninhamento de escopos.
"""

import sys
from lexer.tokens import (
    PR_TREM_DI_NUMERU, PR_TREM_CUM_VIRGULA,
    PR_TREM_DISCRITA, PR_TREM_DISCOLHE, PR_TROSSO,
)


# Mapeamento de tipo → valor inicial padrão.
# Quando uma variável é declarada sem inicialização, ela recebe esse valor.
VALOR_INICIAL_PADRAO = {
    PR_TREM_DI_NUMERU:   0,       # int
    PR_TREM_CUM_VIRGULA: 0.0,     # float
    PR_TREM_DISCRITA:    "",      # string
    PR_TREM_DISCOLHE:    "eh",    # bool (eh = true)
    PR_TROSSO:           "\\0",   # char (caractere nulo)
}


# Mapeamento de tipo → nome legível (para mensagens de erro)
NOME_DO_TIPO = {
    PR_TREM_DI_NUMERU:   "trem_di_numeru",
    PR_TREM_CUM_VIRGULA: "trem_cum_virgula",
    PR_TREM_DISCRITA:    "trem_discrita",
    PR_TREM_DISCOLHE:    "trem_discolhe",
    PR_TROSSO:           "trosso",
}


class TabelaSimbolos:
    """
    Armazena variáveis declaradas e seus metadados.

    Cada entrada é um dicionário com:
        {
            "tipo": código numérico do tipo (PR_TREM_DI_NUMERU, etc.),
            "linha": linha onde foi declarada (para mensagens de erro),
            "coluna": coluna onde foi declarada,
        }
    """

    def __init__(self):
        self.simbolos = {}

    def declarar(self, nome: str, tipo: int, linha: int, coluna: int):
        """
        Registra uma nova variável.

        Levanta erro fatal se a variável já estiver declarada.
        """
        if nome in self.simbolos:
            decl_anterior = self.simbolos[nome]
            self._erro(
                f"Variável '{nome}' já foi declarada anteriormente "
                f"(linha {decl_anterior['linha']}, coluna {decl_anterior['coluna']}).",
                linha, coluna
            )

        self.simbolos[nome] = {
            "tipo":   tipo,
            "linha":  linha,
            "coluna": coluna,
        }

    def existe(self, nome: str) -> bool:
        """Retorna True se a variável foi declarada."""
        return nome in self.simbolos

    def tipo_de(self, nome: str) -> int:
        """Retorna o código do tipo da variável, ou None se não existe."""
        info = self.simbolos.get(nome)
        return info["tipo"] if info else None

    def verificar_uso(self, nome: str, linha: int, coluna: int):
        """
        Garante que a variável foi declarada antes de ser usada.

        Levanta erro fatal se não foi.
        """
        if not self.existe(nome):
            self._erro(
                f"Variável '{nome}' usada sem ter sido declarada.",
                linha, coluna
            )

    def valor_inicial(self, tipo: int):
        """Retorna o valor inicial padrão para um tipo."""
        return VALOR_INICIAL_PADRAO.get(tipo, 0)

    def _erro(self, mensagem: str, linha: int, coluna: int):
        """Dispara erro semântico fatal e aborta a execução."""
        print("\n[ERRO SEMÂNTICO]")
        print(f"Linha: {linha}, Coluna: {coluna}")
        print(mensagem)
        print("Execução abortada.\n")
        sys.exit(1)

    def listar(self) -> dict:
        """Retorna uma cópia da tabela. Útil para debug ou exibição."""
        return dict(self.simbolos)
