import sys
from lexer import Lexer

def formata_saida_vetor(tokens: list) -> str:
    linhas = ["[\n"]
    
    for i, (lexema, codigo, linha, coluna) in enumerate(tokens):
        lex_str = f'"{lexema}"'
        virgula = "," if i < len(tokens) - 1 else ""
        linhas.append(f"\t({lex_str:<20}, {codigo:>3}, {linha}, {coluna:>2}){virgula}\n")

    linhas.append("]")

    return "".join(linhas)

def main():
    arquivo_entrada = "input/entrada.uai"
    arquivo_saida   = "output/saida.uai"

    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            fonte = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo_entrada}' não encontrado.")
        sys.exit(1)

    lexer   = Lexer(fonte)
    sucesso = lexer.tokenizar()

    saida_vetor = formata_saida_vetor(lexer.tokens)
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(saida_vetor)

    if not sucesso:
        sys.exit(1)

if __name__ == "__main__":
    main()