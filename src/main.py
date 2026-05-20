# src/main.py
import os
import sys
from lexer.lexer import Lexer, formata_tokens
from parser.parser import Parser
from ir import formata_codigo
from interpreter.interpreter import Interpretador

def clear_console():
    print("\n" * 100)
    os.system('cls' if os.name == 'nt' else 'clear')

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

def analise_sintatica(tokens: list) -> list:
    parser = Parser(tokens)
    codigo_ir = parser.iniciar()
    print("  [PARSER] Análise sintática concluída com sucesso!")
    return codigo_ir

def gera_ir(codigo_ir: list, arquivo_saida: str):
    if not codigo_ir:
        print("  [IR] Nenhum código intermediário a gerar.")
        return

    os.makedirs(os.path.dirname(arquivo_saida), exist_ok=True)
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(formata_codigo(codigo_ir))
    print(f"  [IR] Sucesso! {len(codigo_ir)} tuplas geradas, salvas em {arquivo_saida}.")

def main():
    clear_console()
    print("-"*40)
    print(" "*11 +  "MINERES INTERPRETER")
    print("-"*40 + "\n")
    
    # Configuração de caminhos
    arquivo_entrada     = "data/input/entrada.uai"
    arquivo_saida       = "data/output/saida.uai"
    arquivo_saida_ir    = "data/output/saida_ir.uai"

    print(f"  Arquivo de entrada: {arquivo_entrada}")
    print(f"  Saída léxica      : {arquivo_saida}")
    print(f"  Saída IR          : {arquivo_saida_ir}\n")

    # Leitura do arquivo
    fonte = read_file(arquivo_entrada)

    # ----------------------------------- 
    # Análise Léxica
    print(" "*7 + "-" * 5 + " ANÁLISE LÉXICA (LEXER) " + "-" * 5)
    tokens = analise_lexica(fonte, arquivo_saida)
    print("\n" + "-"*40 + "\n")

    # -----------------------------------
    # Análise Sintática
    print(" "*7 + "-" * 5 + " ANÁLISE SINTÁTICA (PARSER) " + "-" * 5)
    codigo_ir = analise_sintatica(tokens)
    print("\n" + "-"*40 + "\n")

    # -----------------------------------
    # Geração de Código Intermediário
    print(" "*2 + "-" * 5 + " GERAÇÃO DE CÓDIGO INTERMEDIÁRIO " + "-" * 5)
    gera_ir(codigo_ir, arquivo_saida_ir)
    print("\n" + "-"*40 + "\n")

    # -----------------------------------
    # Execução (Máquina Virtual)
    print(" "*10 + "-" * 5 + " INTERPRETADOR " + "-" * 5)
    if codigo_ir:
        vm = Interpretador(codigo_ir)
        vm.executar()
    else:
        print("  [VM] Execução ignorada (código IR vazio).")
    print("\n" + "-"*40 + "\n")

    # -----------------------------------
    # Fim
    print(" "*6 + "-" * 10 + " FIM " + "-" * 10)

if __name__ == "__main__":
    main()