import sys
from lexer import Lexer
import os

def formata_saida_vetor(tokens: list) -> str:
    linhas = ["[\n"]
    
    for i, (lexema, codigo, linha, coluna) in enumerate(tokens):
        lex_str = f'"{lexema}"'
        virgula = "," if i < len(tokens) - 1 else ""
        linhas.append(f"\t({lex_str:<20}, {codigo:>3}, {linha}, {coluna:>2}){virgula}\n")

    linhas.append("]")

    return "".join(linhas)

def print_lista_tokens(saida_vetor: str, arquivo_entrada: str, arquivo_saida: str = "output/saida.uai"):
    print("="*60)
    print("                     LISTA DE TOKENS")
    print("="*60)

    print("  -> ENTRADA: ", arquivo_entrada)
    print("  -> SAÍDA:   ", arquivo_saida)
    print("\n  -> Formato: (\"lexema\", código, linha, coluna)\n")
    print("-"*60)

    print("\n")

    print(saida_vetor)


def main():
    os.makedirs("output", exist_ok=True)

    arquivo_entrada = "input/entrada.uai"
    arquivo_saida   = "output/saida.uai"

    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            fonte = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{arquivo_entrada}' não encontrado.")
        sys.exit(1)

    lexer = Lexer(fonte)

    #contagem de tempo de execução do lexer
    import time
    start_time = time.time()
    lexer.tokenizar()
    end_time = time.time()

    print(f"Tempo de execução do lexer: {end_time - start_time:.10f} segundos")

    saida_vetor = formata_saida_vetor(lexer.tokens)

    # print_lista_tokens(saida_vetor, arquivo_entrada, arquivo_saida)

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(saida_vetor)

if __name__ == "__main__":
    main()