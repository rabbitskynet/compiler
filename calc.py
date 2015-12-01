# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
# -----------------------------------------------------------------------------
import sys
sys.path.insert(0,"../..")

if sys.version_info[0] >= 3:
	raw_input = input

tokens = (
	'LPAREN','RPAREN','NUMBER',
	)

literals = ['=','+','-','*','/', '(',')']

# Tokens

import random

class Exp: pass

class Node(Exp):
	def __init__(self, tokenname, value1 = None, operand = None, value2 = None):
		self.name = random.getrandbits(64)
		self.token = tokenname
		self.left = value1
		self.right = value2
		self.op = operand

t_LPAREN	= r'\('
t_RPAREN	= r'\)'

def t_NUMBER(t):
	r'\d+'
	t.value = int(t.value)
	return t

t_ignore = " \t"

def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex()

# Parsing rules

precedence = (
	('left','+','-'),
	('left','*','/'),
	)

def p_expression_binop(p):
	'''expression : expression '+' expression
				  | expression '-' expression
				  | expression '*' expression
				  | expression '/' expression'''
	p[0] = Node('binary-expression',p[1],p[2],p[3])

def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	p[0] = Node('group-expression',p[2])

def p_expression_number(p):
	'expression : NUMBER'
	p[0] = Node('number-expression',p[1])

def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
	else:
		print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()

def getItem(fileH, parent, array, level):
	level += 1
	if array.token == 'binary-expression':
		fileH.write("\t{} [label=\"Bin:{}\"]\n".format(array.name,array.op))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		#~ print array.left,array.right
		getItem(fileH, array.name, array.left, level)
		getItem(fileH, array.name, array.right , level)
	elif array.token == 'number-expression':
		fileH.write("\t{} [label=\"Number:{}\"]\n".format(array.name,array.left))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
	elif array.token == 'group-expression':
		fileH.write("\t{} [label=\"Group\"]\n".format(array.name))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		getItem(fileH, array.name, array.left, level)
#dot -Tjpg -o file.jpg graph.gv

while 1:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	res = yacc.parse(s)
	fileH = open("graph.gv", 'w')
	fileH.write("digraph G {\n")
	getItem(fileH, "start", res, -1)
	fileH.write("}\n")
#	getItem(res,-1)
	#~ print res
#	t = Tree(ar)
#	t.show()

