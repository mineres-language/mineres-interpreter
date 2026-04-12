# src/main.py
import os
import sys
from lexer.lexer import Lexer, formata_tokens
from parser.parser import Parser

def read_file(arquivo_entrada: str) -> str:
    try:
        with open(arquivo_entrada, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado, uai!")
        sys.exit(1)

def analise_lexica(fonte: str, arquivo_saida: str) -> list:
    lexer = Lexer(fonte)
    if lexer.tokenizar():
        os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write(formata_tokens(lexer.tokens))
        print(f"  [LEXER] Sucesso! {len(lexer.tokens)} tokens gerados, tokens salvos em {arquivo_saida}.")
        return lexer.tokens
    else:
        print("  [LEXER] Falha na análise léxica.")
        sys.exit(1)

def analise_sintatica(tokens: list):
    parser = Parser(tokens)
    if parser.iniciar():
        print("  [PARSER] Análise sintática concluída com sucesso!")
    else:
        print("  [PARSER] Falha na análise sintática.")
        sys.exit(1)

def main():
    print("-"*40)
    print(" "*11 +  "MINERES INTERPRETER" + " "*11)
    print("-"*40 + "\n")
    
    # Configuração de caminhos
    arquivo_entrada = "data/input/entrada.uai"
    arquivo_saida   = "data/output/saida.uai"

    print(f"  Arquivo de entrada: {arquivo_entrada}")
    print(f"  Arquivo de saída: {arquivo_saida}\n")

    # Leitura do arquivo
    fonte = read_file(arquivo_entrada)

    # ----------------------------------- 
    # Análise Léxica
    print(" "*7 + "-" * 5 + " ANÁLISE LEXER " + "-" * 5)
    tokens = analise_lexica(fonte, arquivo_saida)
    

    print("\n" + "-"*40 + "\n")

    # -----------------------------------
    # Análise Sintática
    print(" "*2 + "-" * 5 + " ANÁLISE PARSER (SINTÁTICA) " + "-" * 5)
    analise_sintatica(tokens)


    # (Próxima etapa)

if __name__ == "__main__":
    main()