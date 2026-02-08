from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .erros import ErroLexico, Posicao


@dataclass(frozen=True)
class Token:
    tipo: str
    lexema: str
    linha: int
    coluna: int


class Lexer:
    """
    Lexer (analisador léxico) para um subset de Portugol.
    Transforma texto em uma sequência de Tokens.
    """

    # Palavras-chave do Portugol (subset do enunciado)
    KEYWORDS = {
        "inteiro": "KW_INTEIRO",
        "real": "KW_REAL",
        "cadeia": "KW_CADEIA",
        "se": "KW_SE",
        "entao": "KW_ENTAO",
        "senao": "KW_SENAO",
        "fimse": "KW_FIMSE",
        "enquanto": "KW_ENQUANTO",
        "faca": "KW_FACA",
        "fimenquanto": "KW_FIMENQUANTO",
        "procedimento": "KW_PROCEDIMENTO",
        "funcao": "KW_FUNCAO",
        "inicio": "KW_INICIO",
        "fim": "KW_FIM",
        "retorne": "KW_RETORNE",
        "escreva": "KW_ESCREVA",
    }

    # Especificação (tipo_token, regex) em ordem de prioridade
    TOKEN_SPECS: list[tuple[str, str]] = [
        # especiais
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t\r]+"),
        ("COMMENT", r"//[^\n]*"),
        # literais
        ("STRING", r"\"([^\"\\]|\\.)*\""),
        ("NUM_REAL", r"\d+\.\d+"),
        ("NUM_INT", r"\d+"),
        # operadores (incluindo relacionais)
        ("EQ", r"=="),
        ("NE", r"!="),
        ("LE", r"<="),
        ("GE", r">="),
        ("LT", r"<"),
        ("GT", r">"),
        ("ASSIGN", r"="),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        # delimitadores
        ("SEMI", r";"),
        ("COMMA", r","),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        # identificadores
        ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ]

    def __init__(self) -> None:
        parts = []
        for tok_type, pattern in self.TOKEN_SPECS:
            parts.append(f"(?P<{tok_type}>{pattern})")
        self._master_pat = re.compile("|".join(parts))

    def tokenizar(self, codigo: str) -> list[Token]:
        tokens: list[Token] = []
        linha = 1
        coluna = 1
        pos = 0
        n = len(codigo)

        while pos < n:
            m = self._master_pat.match(codigo, pos)
            if not m:
                # Caractere inválido
                ch = codigo[pos]
                raise ErroLexico(
                    f"Caractere inesperado: {repr(ch)}",
                    Posicao(linha, coluna),
                )

            kind = m.lastgroup
            lex = m.group(kind)
            start = pos
            pos = m.end()

            if kind == "NEWLINE":
                linha += 1
                coluna = 1
                continue

            if kind in ("SKIP", "COMMENT"):
                # atualiza coluna pelo tamanho do lexema ignorado
                coluna += pos - start
                continue

            tok_linha = linha
            tok_coluna = coluna

            # Atualiza coluna depois de consumir o lexema
            coluna += pos - start

            if kind == "IDENT":
                lowered = lex.lower()
                if lowered in self.KEYWORDS:
                    kind = self.KEYWORDS[lowered]

            tokens.append(Token(kind, lex, tok_linha, tok_coluna))

        tokens.append(Token("EOF", "", linha, coluna))

        return tokens
