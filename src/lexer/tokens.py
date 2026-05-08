# =============================================================================
# CÓDIGOS DOS TOKENS
# =============================================================================

# Palavras Reservadas (100–199)
PR_TREM_DI_NUMERU   = 100
PR_TREM_CUM_VIRGULA = 101
PR_TREM_DISCRITA    = 102
PR_TREM_DISCOLHE    = 103
PR_TROSSO           = 104

PR_UAI_SE           = 110
PR_UAI_SENAO        = 111
PR_DEPENDENU        = 112
PR_DU_CASU          = 113
PR_UAI_SO           = 114

PR_RODA_ESSE_TREM   = 120
PR_ENQUANTO         = 121
PR_PARA_O_TREM      = 122
PR_TOCA_O_TREM      = 123

PR_BORA_CUMPADE     = 130
PR_TA_BAO           = 131
PR_MAIN             = 132

# Booleanos (junto das Palavras Reservadas)
PR_EH               = 133
PR_NUM_EH           = 134

PR_OIA_PROCE_VE     = 140
PR_XOVE             = 141

# Literais (200–299)
LIT_NUM_INT         = 200
LIT_NUM_HEX         = 201
LIT_NUM_OCT         = 202
LIT_NUM_FLOAT       = 203
LIT_STRING          = 204
LIT_CHAR            = 205

# Identificadores (300)
IDENTIFICADOR       = 300

# Operadores (400–499)
OP_FICA_ASSIM_ENTAO = 400
OP_MEMA_COISA       = 401
OP_NEH_NADA         = 402
OP_MENOR            = 403
OP_MAIOR            = 404
OP_MENOR_IGUAL      = 405
OP_MAIOR_IGUAL      = 406

OP_MAIS             = 410
OP_MENOS            = 411
OP_VEIZ             = 412
OP_SOB              = 413
OP_MODULO           = 414

OP_TAMEM            = 420
OP_QUARQUE_UM       = 421
OP_VAM_MARCA        = 422
OP_UM_O_OTO         = 423

# Delimitadores (500–599)
DEL_SIMBORA         = 500
DEL_CABO            = 501
DEL_UAI             = 502
DEL_ABRE_PAR        = 503
DEL_FECHA_PAR       = 504
DEL_VIRGULA         = 505

# # Erros (900–999)
# ERRO_STRING         = 900
# ERRO_NUMERO         = 901
# ERRO_SIMBOLO        = 902
# ERRO_CAUSO          = 903

# Novos Operadores e Delimitadores
OP_DIVISAO_INT      = 415
DEL_ABRE_CHAVE      = 506
DEL_FECHA_CHAVE     = 507
DEL_PONTO           = 508
DEL_PONTO_VIRGULA   = 509
DEL_DOIS_PONTOS     = 510

# =============================================================================
# TABELA DE PALAVRAS RESERVADAS E OPERADORES TEXTUAIS
# Mapeamento: lexema (str) → código (int)
# =============================================================================

PALAVRAS_RESERVADAS = {
    # Estruturas de Controle
    "uai_se":             PR_UAI_SE,
    "uai_senao":          PR_UAI_SENAO,
    "roda_esse_trem":     PR_RODA_ESSE_TREM,
    "enquanto_tiver_trem":PR_ENQUANTO,
    "dependenu":          PR_DEPENDENU,
    "du_casu":            PR_DU_CASU,
    "uai_so":             PR_UAI_SO,
    # Fluxo e Funções
    "ta_bao":             PR_TA_BAO,
    "para_o_trem":        PR_PARA_O_TREM,
    "toca_o_trem":        PR_TOCA_O_TREM,
    "bora_cumpade":       PR_BORA_CUMPADE,
    "main":               PR_MAIN,
    # Variáveis e Dados
    "trem_di_numeru":     PR_TREM_DI_NUMERU,
    "trem_cum_virgula":   PR_TREM_CUM_VIRGULA,
    "trem_discrita":      PR_TREM_DISCRITA,
    "trem_discolhe":      PR_TREM_DISCOLHE,
    "trosso":             PR_TROSSO,
    "eh":                 PR_EH,
    "num_eh":             PR_NUM_EH,
    # Escopo e Sintaxe
    "simbora":            DEL_SIMBORA,
    "cabo":               DEL_CABO,
    "uai":                DEL_UAI,
    # Operadores Relacionais
    "fica_assim_entao":   OP_FICA_ASSIM_ENTAO,
    "neh_nada":           OP_NEH_NADA,
    "mema_coisa":         OP_MEMA_COISA,
    # Operadores Lógicos
    "quarque_um":         OP_QUARQUE_UM,
    "vam_marca":          OP_VAM_MARCA,
    "tamem":              OP_TAMEM,
    "um_o_oto":           OP_UM_O_OTO,
    # Operadores Aritméticos
    "veiz":               OP_VEIZ,
    "sob":                OP_SOB,
    # Entrada e Saída
    "xove":               PR_XOVE,
    "oia_proce_ve":       PR_OIA_PROCE_VE,    
}

# =============================================================================
# DICIONÁRIO REVERSO (Para mensagens de erro automáticas no Parser)
# =============================================================================

NOMES_TOKENS = {
    IDENTIFICADOR: "Identificador (nome de variável/função)",
    LIT_NUM_INT: "Número Inteiro",
    LIT_NUM_HEX: "Número Hexadecimal",
    LIT_NUM_OCT: "Número Octal",
    LIT_NUM_FLOAT: "Número Decimal (Float)",
    LIT_STRING: "Texto (String)",
    LIT_CHAR: "Caractere (Char)",
    
    # Delimitadores e Operadores extras que não são palavras
    DEL_ABRE_PAR: "'('",
    DEL_FECHA_PAR: "')'",
    DEL_VIRGULA: "','",
    DEL_ABRE_CHAVE: "'{'",
    DEL_FECHA_CHAVE: "'}'",
    DEL_PONTO: "'.'",
    DEL_PONTO_VIRGULA: "';'",
    DEL_DOIS_PONTOS: "':'",
    OP_MENOR_IGUAL: "'<='",
    OP_MENOR: "'<'",
    OP_MAIOR_IGUAL: "'>='",
    OP_MAIOR: "'>'",
    OP_MAIS: "'+'",
    OP_MENOS: "'-'",
    OP_MODULO: "'%'",
    OP_DIVISAO_INT: "'/'",
}

for lexema, codigo in PALAVRAS_RESERVADAS.items():
    NOMES_TOKENS[codigo] = f"'{lexema}'"