from src.lexer import Lexer
from src.erros import ErroCompilador

codigo = """
inteiro a;
inteiro b;
a = 2 + 3 * 4;
b = (2 + 3) * 4;
escreva(a);
escreva(b);
"""

print("\npara o código:\n")
print("=============================")
print(codigo)
print("=============================\n")

try:
    tokens = Lexer().tokenizer(codigo)

    for token in tokens:
        print(token)
except ErroCompilador as e:
    print(e)
