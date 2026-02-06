from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser
from src.erros import ErroCompilador

codigo = """
inteiro x;
x = 10;

se (x > 10) entao
  x = x + 1;
senao
  x = 0;
fimse

enquanto (x < 5) faca
  x = x + 1;
fimenquanto

escreva(x);
"""

print("\npara o código:\n")
print("=============================")
print(codigo)
print("=============================\n")

try:
    tokens = Lexer().tokenizar(codigo)
    arvore = Parser(tokens).parse()

    print("------- TOKENS -------")
    for token in tokens:
        print(token)

    print("\n------- AST -------")
    pprint(arvore)

except ErroCompilador as e:
    print(e)
