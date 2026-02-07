from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SimboloVar:
    kind: str
    nome: str
    tipo: str


@dataclass(frozen=True)
class SimboloRotina:
    kind: str
    nome: str
    params: list[str]
    retorno: str | None


class TabelaDeSimbolos:
    def __init__(self) -> None:
        self._scopes: list[dict[str, object]] = [dict()]

    def push(self) -> None:
        self._scopes.append(dict())

    def pop(self) -> None:
        if len(self._scopes) == 1:
            raise RuntimeError("Não é permitido remover o escopo global.")
        self._scopes.pop()

    def declarar_var(self, nome: str, tipo: str) -> None:
        atual = self._scopes[-1]
        if nome in atual:
            raise ValueError(f"Identificador '{nome}' já declarado neste escopo.")
        atual[nome] = SimboloVar(kind="var", nome=nome, tipo=tipo)

    def declarar_rotina(
        self, nome: str, kind: str, params: list[str], retorno: str | None
    ) -> None:
        atual = self._scopes[0]
        if nome in atual:
            raise ValueError(f"Rotina '{nome}' já declarada.")
        atual[nome] = SimboloRotina(
            kind=kind, nome=nome, params=params, retorno=retorno
        )

    def buscar(self, nome: str):
        for scope in reversed(self._scopes):
            if nome in scope:
                return scope[nome]
        return None
