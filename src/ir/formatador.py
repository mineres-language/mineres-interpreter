"""
Formatador da saída final do código intermediário.

Converte a lista de tuplas Python em uma string formatada que vai
para o arquivo data/output/saida_ir.uai.

Convenções de saída:
    - Tuplas no formato (op, a, b, c)
    - Valores None são impressos como "null"
    - Strings são preservadas com aspas
    - Inteiros e floats são impressos sem aspas
"""


def formata_valor(valor) -> str:
    """
    Converte um valor Python na sua representação textual para o IR.

    Regras:
        - None       → "null"
        - str        → "valor" (com aspas)
        - bool/int/float → repr direto

    Strings com caracteres especiais (já escapados) são preservadas.
    """
    if valor is None:
        return "null"
    if isinstance(valor, str):
        return f'"{valor}"'
    return str(valor)


def formata_tupla(tupla: tuple) -> str:
    """Formata uma única tupla do IR."""
    partes = [formata_valor(v) for v in tupla]
    return f"({', '.join(partes)})"


def formata_codigo(lista_tuplas: list) -> str:
    """
    Formata a lista completa de tuplas como saída final.

    A saída tem uma tupla por linha, dentro de colchetes,
    seguindo o mesmo padrão visual do saida.uai dos tokens.
    """
    if not lista_tuplas:
        return "[]"

    linhas = ["["]
    for i, tupla in enumerate(lista_tuplas):
        virgula = "," if i < len(lista_tuplas) - 1 else ""
        linhas.append(f"\t{formata_tupla(tupla)}{virgula}")
    linhas.append("]")

    return "\n".join(linhas)
