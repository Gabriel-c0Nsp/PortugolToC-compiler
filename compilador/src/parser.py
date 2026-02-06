from __future__ import annotations

from .lexer import Token
from .erros import ErroSintatico, Posicao
from .ast_nodes import (
    Program,
    VarDecl,
    Assign,
    Write,
    Expr,
    Compare,
    If,
    While,
    NumInt,
    NumReal,
    StrLit,
    VarRef,
    BinOp,
)


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def match(self, tipo: str) -> bool:
        return self.current().tipo == tipo

    def eat(self, tipo: str) -> Token:
        token = self.current()

        if token.tipo != tipo:
            raise ErroSintatico(
                f"Esperado {tipo}, mas veio {token.tipo} ({token.lexema})",
                Posicao(token.linha, token.coluna),
            )

        self.pos += 1

        return token

    def parse(self) -> Program:
        comandos = []

        while not self.match("EOF"):
            comandos.append(self.comando())
        self.eat("EOF")

        return Program(comandos)

    def comando(self):
        token = self.current()

        if token.tipo in ("KW_INTEIRO", "KW_REAL", "KW_CADEIA"):
            return self.declaracao()

        if token.tipo == "KW_ESCREVA":
            return self.escreva_stmt()

        if token.tipo == "KW_SE":
            return self.se_stmt()

        if token.tipo == "KW_ENQUANTO":
            return self.enquanto_stmt()

        if token.tipo == "IDENT":
            return self.atribuicao()

        raise ErroSintatico(
            f"Comando inválido começando em {token.tipo} ({token.lexema})",
            Posicao(token.linha, token.coluna),
        )

    def declaracao(self) -> VarDecl:
        if self.match("KW_INTEIRO"):
            self.eat("KW_INTEIRO")
            tipo = "inteiro"
        elif self.match("KW_REAL"):
            self.eat("KW_REAL")
            tipo = "real"
        else:
            self.eat("KW_CADEIA")
            tipo = "cadeia"

        nome = self.eat("IDENT").lexema
        self.eat("SEMI")

        return VarDecl(tipo, nome)

    def atribuicao(self) -> Assign:
        nome = self.eat("IDENT").lexema
        self.eat("ASSIGN")
        expr = self.expr()
        self.eat("SEMI")

        return Assign(nome, expr)

    def escreva_stmt(self) -> Write:
        self.eat("KW_ESCREVA")
        self.eat("LPAREN")
        expr = self.expr()
        self.eat("RPAREN")
        self.eat("SEMI")

        return Write(expr)

    def expr(self) -> Expr:
        node = self.termo()

        while self.match("PLUS") or self.match("MINUS"):

            if self.match("PLUS"):
                self.eat("PLUS")
                op = "+"
            else:
                self.eat("MINUS")
                op = "-"

            right = self.termo()
            node = BinOp(op, node, right)

        return node

    def condicao(self) -> Expr:
        left = self.expr()

        if (
            self.match("GT")
            or self.match("LT")
            or self.match("GE")
            or self.match("LE")
            or self.match("EQ")
            or self.match("NE")
        ):
            if self.match("GT"):
                self.eat("GT")
                op = ">"
            elif self.match("LT"):
                self.eat("LT")
                op = "<"
            elif self.match("GE"):
                self.eat("GE")
                op = ">="
            elif self.match("LE"):
                self.eat("LE")
                op = "<="
            elif self.match("EQ"):
                self.eat("EQ")
                op = "=="
            else:
                self.eat("NE")
                op = "!="
            right = self.expr()
            return Compare(op, left, right)
        return left

    def bloco_ate(self, stop_tokens: set[str]) -> list:
        """
        Lê comandos até o token atual ser um dos stop_tokens (sem consumir o stop token).
        """
        stmts = []

        while (not self.match("EOF")) and (self.current().tipo not in stop_tokens):
            stmts.append(self.comando())
        return stmts

    def se_stmt(self) -> If:
        self.eat("KW_SE")
        self.eat("LPAREN")
        cond = self.condicao()
        self.eat("RPAREN")
        self.eat("KW_ENTAO")

        then_block = self.bloco_ate({"KW_SENAO", "KW_FIMSE"})

        else_block = None
        if self.match("KW_SENAO"):
            self.eat("KW_SENAO")
            else_block = self.bloco_ate({"KW_FIMSE"})

        self.eat("KW_FIMSE")
        return If(cond, then_block, else_block)

    def enquanto_stmt(self) -> While:
        self.eat("KW_ENQUANTO")
        self.eat("LPAREN")
        cond = self.condicao()
        self.eat("RPAREN")
        self.eat("KW_FACA")

        block = self.bloco_ate({"KW_FIMENQUANTO"})

        self.eat("KW_FIMENQUANTO")
        return While(cond, block)

    def termo(self) -> Expr:
        node = self.fator()

        while self.match("MUL") or self.match("DIV"):
            if self.match("MUL"):
                self.eat("MUL")
                op = "*"
            else:
                self.eat("DIV")
                op = "/"

            right = self.fator()
            node = BinOp(op, node, right)

        return node

    def fator(self) -> Expr:
        token = self.current()

        if token.tipo == "NUM_INT":
            self.eat("NUM_INT")
            return NumInt(int(token.lexema))

        if token.tipo == "NUM_REAL":
            self.eat("NUM_REAL")
            return NumReal(float(token.lexema))

        if token.tipo == "STRING":
            self.eat("STRING")
            # remove aspas externas
            return StrLit(token.lexema[1:-1])

        if token.tipo == "IDENT":
            self.eat("IDENT")
            return VarRef(token.lexema)

        if token.tipo == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node

        raise ErroSintatico(
            f"Esperado expressão, mas veio {token.tipo} ({token.lexema})",
            Posicao(token.linha, token.coluna),
        )
