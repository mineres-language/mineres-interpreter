"""Converte a lista de tuplas Python em uma string formatada para o arquivo saida_ir.uai."""


def formata_valor(valor) -> str:
    """None → 'null'; strings sem aspas ganham aspas; números ficam como estão."""
    if valor is None:
        return "null"
    if isinstance(valor, str):
        if valor.startswith('"') or valor.startswith("'") or valor.startswith("@"):
            return valor
        return f'"{valor}"'
    return str(valor)


def formata_tupla(tupla: tuple) -> str:
    """Formata uma única tupla do IR."""
    partes = [formata_valor(v) for v in tupla]
    return f"({', '.join(partes)})"


def formata_codigo(lista_tuplas: list) -> str:
    """Uma tupla por linha dentro de colchetes, mesmo padrão do saida.uai."""
    if not lista_tuplas:
        return "[]"

    linhas = ["["]
    for i, tupla in enumerate(lista_tuplas):
        virgula = "," if i < len(lista_tuplas) - 1 else ""
        linhas.append(f"\t{formata_tupla(tupla)}{virgula}")
    linhas.append("]")

    return "\n".join(linhas)
