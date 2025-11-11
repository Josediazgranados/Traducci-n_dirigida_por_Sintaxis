##Analizador Sintáctico con Árbol Decorado en Python##

Este proyecto implementa un analizador léxico y sintáctico para expresiones aritméticas en Python.
Genera un Árbol Sintáctico Decorado (AST) que muestra la estructura jerárquica de las expresiones y evalúa los valores asociados a cada nodo.
Además, permite visualizar el árbol de manera gráfica utilizando Tkinter.

##Características principales##

Analizador léxico que convierte texto en tokens (NUM, ID, +, -, *, /, =, (, ), $).

Analizador sintáctico descendente recursivo que construye el árbol sintáctico.

Evaluación semántica integrada: cada nodo del árbol contiene el valor calculado.

Tabla de símbolos para registrar variables y sus valores.

Visualización interactiva del árbol sintáctico decorado con Tkinter.

Lectura automática de expresiones desde un archivo de texto.

##Ejecución del programa##

python main_unido.py
