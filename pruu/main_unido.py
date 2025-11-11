import tkinter as tk
import math

class SymbolTable:
    def __init__(self):
        self._table = {}

    def add(self, name, entry):
        if name in self._table:
            raise KeyError(f"Simbolo {name} ya existe")
        self._table[name] = entry

    def get(self, name):
        return self._table.get(name)

    def __repr__(self):
        s = "Tabla de simbolos:\n"
        for k, v in self._table.items():
            s += f"  {k} -> {v}\n"
        return s


DIGITS = "0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Token:
    def __init__(self, kind: str, lex: str):
        self.kind = kind
        self.lex = lex

    def __repr__(self):
        return f"Token({self.kind}, {self.lex})"

def tokenize(input_text: str):
    tokens = []
    i = 0
    n = len(input_text)
    while i < n:
        ch = input_text[i]

        if ch.isspace():
            i += 1
            continue

        if ch in '+-*/()=':
            tokens.append(Token(ch, ch))
            i += 1
            continue

        if ch in DIGITS:
            j = i
            while j < n and input_text[j] in DIGITS:
                j += 1
            lex = input_text[i:j]
            tokens.append(Token('NUM', lex))
            i = j
            continue

        if ch in LETTERS:
            j = i
            while j < n and (input_text[j] in LETTERS or input_text[j] in DIGITS or input_text[j] == '_'):
                j += 1
            lex = input_text[i:j]
            tokens.append(Token('ID', lex))
            i = j
            continue

        raise SyntaxError(f"Caracter invalido en input: '{ch}' en posicion {i}")

    tokens.append(Token('$', '$'))
    return tokens

class ASTNode:
    def __init__(self, kind, children=None, lex=None):
        self.kind = kind
        self.children = children if children is not None else []
        self.lex = lex
        self.val = None

    def __repr__(self):
        if self.lex:
            return f"ASTNode({self.kind},{self.lex},{self.val})"
        return f"ASTNode({self.kind},{self.val})"

def print_ast(node, indent=0):
    pad = "  " * indent
    if node.lex:
        print(f"{pad}{node.kind} (lex={node.lex}) val={node.val}")
    else:
        print(f"{pad}{node.kind} val={node.val}")
    for child in node.children:
        print_ast(child, indent + 1)

class Parser:
    def __init__(self, tokens, tabla: SymbolTable):
        self.tokens = tokens
        self.i = 0
        self.tabla = tabla

    def current(self):
        return self.tokens[self.i]

    def advance(self):
        if self.i < len(self.tokens) - 1:
            self.i += 1

    def match(self, kind):
        if self.current().kind == kind:
            tok = self.current()
            self.advance()
            return tok
        raise SyntaxError(f"Se esperaba '{kind}', se encontro '{self.current().lex}'")

    def parse_S(self):
        if self.current().kind == 'ID':
            id_token = self.match('ID')
            self.match('=')
            expr_node = self.parse_E()

            self.tabla.add(id_token.lex, {'tipo': 'int', 'valor': expr_node.val})

            node = ASTNode('assign', [expr_node], id_token.lex)
            node.val = expr_node.val
            return node
        else:
            return self.parse_E()

    def parse_E(self):
        left = self.parse_T()
        while self.current().kind in ('+', '-'):
            op = self.current().kind
            self.advance()
            right = self.parse_T()
            node = ASTNode(op, [left, right])
            if op == '+':
                node.val = left.val + right.val
            else:
                node.val = left.val - right.val
            left = node
        return left

    def parse_T(self):
        left = self.parse_F()
        while self.current().kind in ('*', '/'):
            op = self.current().kind
            self.advance()
            right = self.parse_F()
            node = ASTNode(op, [left, right])
            if op == '*':
                node.val = left.val * right.val
            else:
                node.val = left.val / right.val
            left = node
        return left

    def parse_F(self):
        tok = self.current()
        if tok.kind == 'NUM':
            self.advance()
            node = ASTNode('NUM', [], tok.lex)
            node.val = int(tok.lex)
            return node
        elif tok.kind == 'ID':
            self.advance()
            sym = self.tabla.get(tok.lex)
            if sym is None:
                raise NameError(f"Variable '{tok.lex}' no definida")
            node = ASTNode('ID', [], tok.lex)
            node.val = sym['valor']
            return node
        elif tok.kind == '(':
            self.advance()
            node_e = self.parse_E()
            self.match(')')
            node = ASTNode('()', [node_e])
            node.val = node_e.val
            return node
        else:
            raise SyntaxError(f"Token inesperado en F: {tok.lex}")

    def parse(self):
        node = self.parse_S()
        if self.current().kind != '$':
            raise SyntaxError(f"Se esperaba fin de entrada, encontrado: {self.current().lex}")
        return node


NODE_RADIUS = 25
X_SPACING = 60
Y_SPACING = 80

class ASTVisualizer(tk.Tk):
    def __init__(self, root_node):
        super().__init__()
        self.title("arbol Sintactico Decorado (AST)")
        self.canvas = tk.Canvas(self, width=1200, height=700, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.root_node = root_node
        self.draw_tree(self.root_node, 600, 50, 300)

    def draw_tree(self, node, x, y, offset):
        label = f"{node.kind}\nval={node.val}" if node.val is not None else node.kind
        self.canvas.create_oval(x-NODE_RADIUS, y-NODE_RADIUS, x+NODE_RADIUS, y+NODE_RADIUS,
                                fill="#cce5ff", outline="black")
        self.canvas.create_text(x, y, text=label, font=("Arial", 9))

        if not node.children:
            return

        num_children = len(node.children)
        step = offset / max(num_children - 1, 1)
        start_x = x - offset / 2

        for i, child in enumerate(node.children):
            child_x = start_x + i * step
            child_y = y + Y_SPACING
            self.canvas.create_line(x, y + NODE_RADIUS, child_x, child_y - NODE_RADIUS, arrow=tk.LAST)
            self.draw_tree(child, child_x, child_y, offset / 2)

def mostrar_ast(root_node):
    app = ASTVisualizer(root_node)
    app.mainloop()


def leer_expresiones(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == "__main__":
    tabla = SymbolTable()
    expresiones = leer_expresiones("datos.txt")

    for expr in expresiones:
        print("Expresion:", expr)

        tokens = tokenize(expr)
        print("Tokens generados:", tokens)

        parser = Parser(tokens, tabla)
        ast = parser.parse()

        print("\narbol Sintactico Decorado (AST):")
        print_ast(ast)
        print("\nValor final:", ast.val)

        mostrar_ast(ast)

    print("Tabla de simbolos global:")
    print(tabla)
