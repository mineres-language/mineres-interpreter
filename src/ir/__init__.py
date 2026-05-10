"""Módulo IR (Intermediate Representation)."""

from .geradores import GeradorTemp, GeradorLabel
from .tabela_simbolos import TabelaSimbolos, NOME_DO_TIPO
from .formatador import formata_codigo, formata_tupla, formata_valor

__all__ = [
    "GeradorTemp",
    "GeradorLabel",
    "TabelaSimbolos",
    "NOME_DO_TIPO",
    "formata_codigo",
    "formata_tupla",
    "formata_valor",
]
