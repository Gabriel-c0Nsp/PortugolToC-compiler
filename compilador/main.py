from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser
from src.semantico import AnalisadorSemantico
from src.gerador_c import GeradorC
from src.erros import ErroCompilador

codigo = """
funcao soma(a, b)
inicio
  retorne a + b;
fim

inteiro x;
x = soma(2, 3);
escreva(x);
"""

print("\npara o código:\n")
print("=============================")
print(codigo)
print("=============================\n")

try:
    tokens = Lexer().tokenizar(codigo)
    arvore = Parser(tokens).parse()

    semantica = AnalisadorSemantico()
    semantica.analisar(arvore)

    gerador = GeradorC(semantica.tabela, semantica.tipos_expr)
    codigo_c = gerador.gerar(arvore)

    print("------- TOKENS -------")
    for token in tokens:
        print(token)

    print("\n------- AST -------")
    pprint(arvore)

    print("\n------- C -------")
    print(codigo_c)

except ErroCompilador as e:
    print(e)
