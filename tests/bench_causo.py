"""
[FIX]: Melhorar custo dentro do causo #procura fim do causo (linha 88)

Benchmark do comentário de bloco (causo ... fim_do_causo).

Compara o tempo de tokenização com comentários de tamanhos crescentes.
Execute este arquivo a partir da raiz do projeto:
    python tests/bench_causo.py
"""
import sys
import os
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))

from lexer.lexer import Lexer


def gera_fonte_com_causo(tamanho_comentario: int) -> str:
    """
    Gera um programa Mineres com um comentário de bloco contendo
    `tamanho_comentario` caracteres dentro dele.
    """
    # mistura de caracteres "interessantes" pro lexer:
    # - inclui 'f' várias vezes (testa o falso positivo do 'fim...')
    # - inclui quebras de linha (testa contagem de linhas)
    # - inclui letras que poderiam parecer keywords
    base = "fffabc trem uai cabo simbora roda esse trem\n" * 100
    # repete até atingir o tamanho desejado
    multiplicador = max(1, tamanho_comentario // len(base))
    miolo = (base * multiplicador)[:tamanho_comentario]

    return (
        "bora_cumpade main()\n"
        "simbora\n"
        f"    causo {miolo} fim_do_causo\n"
        "    trem_di_numeru x uai\n"
        "cabo\n"
    )


def bench(tamanho: int, repeticoes: int = 5) -> float:
    """Roda a tokenização `repeticoes` vezes e retorna o tempo médio."""
    fonte = gera_fonte_com_causo(tamanho)
    tempos = []
    for _ in range(repeticoes):
        lexer = Lexer(fonte)
        inicio = time.perf_counter()
        lexer.tokenizar()
        fim = time.perf_counter()
        tempos.append(fim - inicio)
    return sum(tempos) / len(tempos)


def main():
    print("=" * 60)
    print(" BENCHMARK: comentário de bloco (causo ... fim_do_causo)")
    print("=" * 60)
    print(f"{'Tamanho do causo':>20} | {'Tempo médio (ms)':>20}")
    print("-" * 45)

    tamanhos = [100, 1_000, 10_000, 100_000, 500_000]
    for tam in tamanhos:
        media_s = bench(tam)
        media_ms = media_s * 1000
        print(f"{tam:>20,} | {media_ms:>18.3f}")

    print()
    print("Dica: rode antes E depois da otimização pra comparar.")


if __name__ == "__main__":
    main()