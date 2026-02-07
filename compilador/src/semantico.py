from __future__ import annotations

from .ast_nodes import (
    Program,
    Stmt,
    VarDecl,
    Assign,
    Write,
    If,
    While,
    ProcDecl,
    FuncDecl,
    CallStmt,
    Return,
    Expr,
    NumInt,
    NumReal,
    StrLit,
    VarRef,
    BinOp,
    Compare,
    Call,
    Param,
)
from .erros import ErroCompilador
from .tabela_simbolos import TabelaDeSimbolos, SimboloVar, SimboloRotina


class ErroSemantico(ErroCompilador):
    pass


class AnalisadorSemantico:
    def __init__(self) -> None:
        self.tabela = TabelaDeSimbolos()
        self.tipos_expr: dict[int, str] = {}
        self._ctx_func_retorno: str | None = (
            None  # None quando não estamos dentro de função
        )

    def analisar(self, program: Program) -> None:
        for stmt in program.comandos:
            if isinstance(stmt, ProcDecl):
                self._registrar_proc(stmt)
            elif isinstance(stmt, FuncDecl):
                self._registrar_func_stub(stmt)

        for stmt in program.comandos:
            if isinstance(stmt, (ProcDecl, FuncDecl)):
                self._stmt(stmt)

        for stmt in program.comandos:
            if not isinstance(stmt, (ProcDecl, FuncDecl)):
                self._stmt(stmt)

    def _registrar_proc(self, stmt: ProcDecl) -> None:
        tipos = [p.tipo for p in stmt.params]
        try:
            self.tabela.declarar_rotina(
                stmt.nome, kind="proc", params=tipos, retorno=None
            )
        except ValueError as e:
            raise ErroSemantico(str(e))

    def _registrar_func_stub(self, stmt: FuncDecl) -> None:
        # retorno vai ser inferido do 'retorne' durante análise do corpo
        tipos = [p.tipo for p in stmt.params]
        try:
            self.tabela.declarar_rotina(
                stmt.nome, kind="func", params=tipos, retorno=None
            )
        except ValueError as e:
            raise ErroSemantico(str(e))

    # Statements
    def _stmt(self, stmt: Stmt) -> None:
        if isinstance(stmt, VarDecl):
            return self._var_decl(stmt)
        if isinstance(stmt, Assign):
            return self._assign(stmt)
        if isinstance(stmt, Write):
            return self._write(stmt)
        if isinstance(stmt, If):
            return self._if(stmt)
        if isinstance(stmt, While):
            return self._while(stmt)

        if isinstance(stmt, ProcDecl):
            return self._proc_decl(stmt)
        if isinstance(stmt, FuncDecl):
            return self._func_decl(stmt)
        if isinstance(stmt, CallStmt):
            return self._call_stmt(stmt)
        if isinstance(stmt, Return):
            return self._return(stmt)

        raise ErroSemantico(f"Stmt não suportado: {type(stmt).__name__}")

    def _var_decl(self, stmt: VarDecl) -> None:
        try:
            self.tabela.declarar_var(stmt.nome, stmt.tipo)
        except ValueError as e:
            raise ErroSemantico(str(e))

    def _assign(self, stmt: Assign) -> None:
        sym = self.tabela.buscar(stmt.nome)
        if not isinstance(sym, SimboloVar):
            raise ErroSemantico(f"Variável '{stmt.nome}' usada antes de declarar.")

        tipo_expr = self._expr(stmt.expr)
        tipo_var = sym.tipo

        if not self._atribuicao_compativel(tipo_var, tipo_expr):
            raise ErroSemantico(
                f"Atribuição incompatível: variável '{stmt.nome}' é {tipo_var}, expressão é {tipo_expr}."
            )

    def _write(self, stmt: Write) -> None:
        self._expr(stmt.expr)

    def _if(self, stmt: If) -> None:
        tipo_cond = self._expr(stmt.cond)
        if tipo_cond != "bool":
            raise ErroSemantico(f"Condição do 'se' deve ser bool, mas é {tipo_cond}.")

        self.tabela.push()
        for s in stmt.then_block:
            self._stmt(s)
        self.tabela.pop()

        if stmt.else_block is not None:
            self.tabela.push()
            for s in stmt.else_block:
                self._stmt(s)
            self.tabela.pop()

    def _while(self, stmt: While) -> None:
        tipo_cond = self._expr(stmt.cond)
        if tipo_cond != "bool":
            raise ErroSemantico(
                f"Condição do 'enquanto' deve ser bool, mas é {tipo_cond}."
            )

        self.tabela.push()
        for s in stmt.block:
            self._stmt(s)
        self.tabela.pop()

    def _proc_decl(self, stmt: ProcDecl) -> None:
        # novo escopo com parâmetros
        self.tabela.push()
        for p in stmt.params:
            self.tabela.declarar_var(p.nome, p.tipo)

        # procedimento não pode ter return com valor
        old = self._ctx_func_retorno
        self._ctx_func_retorno = None
        for s in stmt.body:
            self._stmt(s)
        self._ctx_func_retorno = old

        self.tabela.pop()

    def _func_decl(self, stmt: FuncDecl) -> None:
        # novo escopo para parâmetros e variáveis locais da função
        self.tabela.push()
        for p in stmt.params:
            self.tabela.declarar_var(p.nome, p.tipo)

        old = self._ctx_func_retorno
        self._ctx_func_retorno = "func"  # estamos dentro de uma função

        retorno_inferido: str | None = None

        for s in stmt.body:
            self._stmt(s)

            if isinstance(s, Return):
                t = self.tipos_expr.get(id(s.expr))
                if t is None:
                    raise ErroSemantico("Tipo do retorno não inferido (erro interno).")

                if retorno_inferido is None:
                    retorno_inferido = t
                else:
                    # Promoção: inteiro + real => real
                    if retorno_inferido == t:
                        pass
                    elif (retorno_inferido, t) in {
                        ("inteiro", "real"),
                        ("real", "inteiro"),
                    }:
                        retorno_inferido = "real"
                    else:
                        raise ErroSemantico(
                            f"Retornos inconsistentes na função '{stmt.nome}': {retorno_inferido} vs {t}."
                        )

        if retorno_inferido is None:
            raise ErroSemantico(f"Função '{stmt.nome}' sem 'retorne'.")

        # atualiza símbolo global da função com o tipo de retorno inferido
        sym = self.tabela.buscar(stmt.nome)
        if not isinstance(sym, SimboloRotina) or sym.kind != "func":
            raise ErroSemantico(
                f"Erro interno: símbolo da função '{stmt.nome}' não encontrado."
            )

        self.tabela._scopes[0][stmt.nome] = SimboloRotina(
            kind="func",
            nome=stmt.nome,
            params=sym.params,
            retorno=retorno_inferido,
        )

        self._ctx_func_retorno = old
        self.tabela.pop()

    def _call_stmt(self, stmt: CallStmt) -> None:
        sym = self.tabela.buscar(stmt.call.nome)
        if not isinstance(sym, SimboloRotina):
            raise ErroSemantico(f"Rotina '{stmt.call.nome}' não declarada.")

        self._checar_args(stmt.call, sym)

    def _return(self, stmt: Return) -> None:
        if self._ctx_func_retorno != "func":
            raise ErroSemantico("'retorne' só é permitido dentro de função.")
        self._expr(stmt.expr)

    # Expressions
    def _expr(self, expr: Expr) -> str:
        if isinstance(expr, NumInt):
            return self._set_tipo(expr, "inteiro")
        if isinstance(expr, NumReal):
            return self._set_tipo(expr, "real")
        if isinstance(expr, StrLit):
            return self._set_tipo(expr, "cadeia")

        if isinstance(expr, VarRef):
            sym = self.tabela.buscar(expr.nome)
            if not isinstance(sym, SimboloVar):
                raise ErroSemantico(f"Variável '{expr.nome}' usada antes de declarar.")
            return self._set_tipo(expr, sym.tipo)

        if isinstance(expr, Call):
            return self._call_expr(expr)

        if isinstance(expr, BinOp):
            t1 = self._expr(expr.left)
            t2 = self._expr(expr.right)
            t = self._tipo_binop(expr.op, t1, t2)
            return self._set_tipo(expr, t)

        if isinstance(expr, Compare):
            t1 = self._expr(expr.left)
            t2 = self._expr(expr.right)
            self._tipo_compare(expr.op, t1, t2)
            return self._set_tipo(expr, "bool")

        raise ErroSemantico(f"Expr não suportada: {type(expr).__name__}")

    def _checar_args(self, call: Call, sym: SimboloRotina) -> None:
        if len(call.args) != len(sym.params):
            raise ErroSemantico(
                f"Chamada de '{call.nome}' com {len(call.args)} args; esperado {len(sym.params)}."
            )

        for i, (arg_expr, tipo_param) in enumerate(zip(call.args, sym.params), start=1):
            tipo_arg = self._expr(arg_expr)
            if not self._atribuicao_compativel(tipo_param, tipo_arg):
                raise ErroSemantico(
                    f"Arg {i} de '{call.nome}' incompatível: esperado {tipo_param}, veio {tipo_arg}."
                )

    def _call_expr(self, call: Call) -> str:
        sym = self.tabela.buscar(call.nome)
        if not isinstance(sym, SimboloRotina):
            raise ErroSemantico(f"Rotina '{call.nome}' não declarada.")

        self._checar_args(call, sym)

        # procedimento
        if sym.kind == "proc":
            raise ErroSemantico(
                f"Procedimento '{call.nome}' não pode ser usado como expressão."
            )

        # função
        if sym.retorno is None:
            raise ErroSemantico(
                f"Tipo de retorno da função '{call.nome}' ainda não definido."
            )

        return self._set_tipo(call, sym.retorno)

    def _set_tipo(self, node: object, tipo: str) -> str:
        self.tipos_expr[id(node)] = tipo
        return tipo

    # Regras de tipos
    def _atribuicao_compativel(self, tipo_var: str, tipo_expr: str) -> bool:
        if tipo_var == tipo_expr:
            return True
        if tipo_var == "real" and tipo_expr == "inteiro":
            return True
        return False

    def _tipo_binop(self, op: str, t1: str, t2: str) -> str:
        if op in {"+", "-", "*", "/"}:
            if t1 == "cadeia" or t2 == "cadeia":
                raise ErroSemantico(f"Operação '{op}' não suportada para cadeia.")
            if t1 == "bool" or t2 == "bool":
                raise ErroSemantico(f"Operação '{op}' não suportada para bool.")
            return "real" if (t1 == "real" or t2 == "real") else "inteiro"
        raise ErroSemantico(f"Operador binário desconhecido: {op}")

    def _tipo_compare(self, op: str, t1: str, t2: str) -> None:
        if t1 == "cadeia" or t2 == "cadeia":
            raise ErroSemantico(f"Comparação '{op}' não suportada para cadeia.")
        if t1 == "bool" or t2 == "bool":
            raise ErroSemantico(f"Comparação '{op}' não suportada para bool.")
