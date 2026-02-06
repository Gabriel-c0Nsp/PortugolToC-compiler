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
    Call,
    Return,
    CallStmt,
    ProcDecl,
    FuncDecl,
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

    def peek(self, k: int = 1) -> Token:
        return self.tokens[self.pos + k]

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

        if token.tipo == "KW_PROCEDIMENTO":
            return self.proc_decl()

        if token.tipo == "KW_FUNCAO":
            return self.func_decl()

        if token.tipo == "KW_RETORNE":
            return self.return_stmt()

        if token.tipo == "IDENT":
            # lookahead 1: se próximo é ASSIGN => atribuicao
            if self.peek().tipo == "ASSIGN":
                return self.atribuicao()
            # se próximo é LPAREN => chamada como comando
            if self.peek().tipo == "LPAREN":
                call = self._call_from_ident()
                self.eat("SEMI")
                return CallStmt(call)
            raise ErroSintatico(
                f"Após identificador '{token.lexema}', esperado '=' ou '('",
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

    def _call_from_ident(self) -> Call:
        nome = self.eat("IDENT").lexema
        self.eat("LPAREN")
        args = []
        if not self.match("RPAREN"):
            args.append(self.expr())
            while self.match("COMMA"):
                self.eat("COMMA")
                args.append(self.expr())
        self.eat("RPAREN")
        return Call(nome, args)

    def _param_list(self) -> list[str]:
        params = []
        if self.match("IDENT"):
            params.append(self.eat("IDENT").lexema)
            while self.match("COMMA"):
                self.eat("COMMA")
                params.append(self.eat("IDENT").lexema)
        return params

    def proc_decl(self) -> ProcDecl:
        self.eat("KW_PROCEDIMENTO")
        nome = self.eat("IDENT").lexema
        self.eat("LPAREN")
        params = self._param_list()
        self.eat("RPAREN")
        self.eat("KW_INICIO")

        body = self.bloco_ate({"KW_FIM"})
        self.eat("KW_FIM")

        return ProcDecl(nome, params, body)

    def func_decl(self) -> FuncDecl:
        self.eat("KW_FUNCAO")
        nome = self.eat("IDENT").lexema
        self.eat("LPAREN")
        params = self._param_list()
        self.eat("RPAREN")
        self.eat("KW_INICIO")

        body = []
        ret = None
        while not self.match("KW_FIM"):
            if self.match("KW_RETORNE"):
                ret = self.return_stmt()
                body.append(ret)
            else:
                body.append(self.comando())

        self.eat("KW_FIM")

        if ret is None:
            tok = self.current()
            raise ErroSintatico(
                f"Função '{nome}' sem 'retorne'.",
                Posicao(tok.linha, tok.coluna),
            )

        return FuncDecl(nome, params, body, ret)

    def return_stmt(self) -> Return:
        tok = self.eat("KW_RETORNE")
        expr = self.expr()
        self.eat("SEMI")
        return Return(expr)

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
            nome = self.eat("IDENT").lexema
            if self.match("LPAREN"):
                self.eat("LPAREN")
                args = []
                if not self.match("RPAREN"):
                    args.append(self.expr())
                    while self.match("COMMA"):
                        self.eat("COMMA")
                        args.append(self.expr())
                self.eat("RPAREN")
                return Call(nome, args)
            return VarRef(nome)

        if token.tipo == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node

        raise ErroSintatico(
            f"Esperado expressão, mas veio {token.tipo} ({token.lexema})",
            Posicao(token.linha, token.coluna),
        )
