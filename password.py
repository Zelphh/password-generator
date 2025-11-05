#!/usr/bin/env python3
"""
gerador_senhas.py

Uso:
    python gerador_senhas.py             # gera 1 senha de 16 caracteres com todas as opções
    python gerador_senhas.py -n 5 -l 20  # gera 5 senhas de 20 caracteres
    python gerador_senhas.py --no-punct  # não usar pontuação
"""

import argparse
import string
import secrets
import sys

# tenta importar pyperclip para copiar ao clipboard (opcional)
try:
    import pyperclip
    _HAS_PYPERCLIP = True
except Exception:
    _HAS_PYPERCLIP = False

# Conjuntos de caracteres
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
PUNCT = string.punctuation

# Caracteres ambíguos frequentemente evitados (0/O, l/1, I, etc.)
AMBIGUOUS = {'0', 'O', 'o', 'I', 'l', '1'}

def build_alphabet(use_lower, use_upper, use_digits, use_punct, exclude_ambiguous):
    parts = []
    if use_lower:
        parts.append(list(LOWER))
    if use_upper:
        parts.append(list(UPPER))
    if use_digits:
        parts.append(list(DIGITS))
    if use_punct:
        parts.append(list(PUNCT))

    alphabet = []
    for p in parts:
        alphabet.extend(p)

    if exclude_ambiguous:
        alphabet = [c for c in alphabet if c not in AMBIGUOUS]

    if not alphabet:
        raise ValueError("Alfabeto vazio: escolha ao menos um tipo de caractere.")

    return alphabet, parts  # parts mantido para garantir pelo menos 1 caractere de cada tipo

def secure_shuffle(lst):
    """Embaralha lista usando SystemRandom (usa os.urandom, seguro)."""
    rand = secrets.SystemRandom()
    rand.shuffle(lst)
    return lst

def generate_password(length=16, use_lower=True, use_upper=True,
                      use_digits=True, use_punct=True, exclude_ambiguous=True):
    if length < 1:
        raise ValueError("Comprimento da senha deve ser >= 1")

    alphabet, parts = build_alphabet(use_lower, use_upper, use_digits, use_punct, exclude_ambiguous)

    # Garantir pelo menos um caractere de cada tipo selecionado (se couber no tamanho)
    required_chars = []
    for part in parts:
        filtered = [c for c in part if (not exclude_ambiguous) or (c not in AMBIGUOUS)]
        if filtered:
            required_chars.append(secrets.choice(filtered))

    if len(required_chars) > length:
        # se o usuário pedir menos caracteres do que o número de categorias, ajustar:
        raise ValueError(f"Length {length} too small for selected character sets ({len(required_chars)} required).")

    # Preenche o restante com escolhas aleatórias do alfabeto total
    remaining = length - len(required_chars)
    result_chars = required_chars + [secrets.choice(alphabet) for _ in range(remaining)]

    # Embaralha para distribuir os required_chars
    secure_shuffle(result_chars)

    return ''.join(result_chars)

def main():
    parser = argparse.ArgumentParser(description="Gerador de senhas seguras (usa secrets).")
    parser.add_argument("-l", "--length", type=int, default=16, help="comprimento da senha (padrão 16)")
    parser.add_argument("-n", "--number", type=int, default=1, help="quantidade de senhas a gerar")
    parser.add_argument("--no-lower", action="store_true", help="não usar letras minúsculas")
    parser.add_argument("--no-upper", action="store_true", help="não usar letras maiúsculas")
    parser.add_argument("--no-digits", action="store_true", help="não usar dígitos")
    parser.add_argument("--no-punct", action="store_true", help="não usar pontuação/símbolos")
    parser.add_argument("--allow-ambiguous", action="store_true", help="permitir caracteres ambíguos (0,O,l,1, etc.)")
    parser.add_argument("--copy", action="store_true", help="tentar copiar a última senha gerada para o clipboard (requer pyperclip)")
    args = parser.parse_args()

    use_lower = not args.no_lower
    use_upper = not args.no_upper
    use_digits = not args.no_digits
    use_punct = not args.no_punct
    exclude_ambiguous = not args.allow_ambiguous

    try:
        for i in range(args.number):
            pwd = generate_password(
                length=args.length,
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_punct=use_punct,
                exclude_ambiguous=exclude_ambiguous
            )
            print(pwd)
        if args.copy:
            if _HAS_PYPERCLIP:
                pyperclip.copy(pwd)  # copia a última gerada
                print("\nÚltima senha copiada para a área de transferência.")
            else:
                print("\npyperclip não encontrado: instale com pip install pyperclip para ativar cópia para clipboard.")
    except ValueError as e:
        print("Erro:", e, file=sys.stderr)
        sys.exit(2)

if _name_ == "_main_":
    main()