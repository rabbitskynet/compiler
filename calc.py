import sys, random

if sys.version_info[0] >= 3:
	raw_input = input

reserved = {
   'for' : 'FOR',
   'do' : 'DO',
   'done' : 'DONE'
}

tokens = [
	'LPAREN','RPAREN', 'ROMAN', 'IDENTIFIER', 'INEQUALITY', 'ASSIGN', 'SEPARATOR'
] + list(reserved.values())

class Exp: pass

class Node(Exp):
	def __init__(self, tokenname, value1 = None, operand = None, value2 = None, value3 = None, value4 = None):
		self.name = random.getrandbits(64)
		self.token = tokenname
		self.left = value1
		self.right = value2
		self.third = value3
		self.four = value4
		self.op = operand

t_LPAREN	= r'\('
t_RPAREN	= r'\)'
t_INEQUALITY   = r'[<\=\>]'
t_SEPARATOR  = r'\;'
t_ASSIGN  = r'\:='
t_ROMAN= r'[VIX][VIX]*'

literals = "+-*/"


def t_COMMENT(t):
	r'\#\#.*\n'
	pass

def t_IDENTIFIER(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	t.type = reserved.get(t.value.lower(),'IDENTIFIER')
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
lines = '\n'.join([line.rstrip('\n') for line in open('code.txt')])
print lines
#data= "VIX + XX for int"
#data=lines
#lexer.input(data)

#exit()
# Tokenize
"""while True:
    tok = lexer.token()
    if not tok:
        break      # No more input
    print(tok)
"""
#exit()


# Parsing rules

precedence = (
	('left','-','+'),
	('left','*','/'),
	)


def p_expression_less(p):
	'expression : expression INEQUALITY expression'
	p[0] = Node('INEQUALITY-expression',p[1],p[2],p[3])

def p_expression_binop(p):
	'''expression : expression '+' expression
				  | expression '-' expression
				  | expression '*' expression
				  | expression '/' expression'''
	p[0] = Node('binary-expression',p[1],p[2],p[3])

def p_expression_for(p):
	'expression : FOR LPAREN expression SEPARATOR expression SEPARATOR expression RPAREN DO expression DONE'
	p[0] = Node('for-expression',p[3],'for',p[5],p[7],p[10])

def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	p[0] = Node('group-expression',p[2])

def p_expression_assign(p):
	'expression : expression ASSIGN expression'
	p[0] = Node('assign-expression',p[1],p[2],p[3])

def p_expression_roman(p):
	'expression : ROMAN'
	p[0] = Node('roman-expression',p[1])

def p_expression_id(p):
	'expression : IDENTIFIER'
	p[0] = Node('id-expression',p[1])

def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
	else:
		print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()

#exit()

res = yacc.parse(lines)
print res.token
print res.left.token
print res.right.token
print res.third.token
print res.four.token

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
"""
#	fileH = open("graph.gv", 'w')
#	fileH.write("digraph G {\n")
#	getItem(fileH, "start", res, -1)
#	fileH.write("}\n")
#	getItem(res,-1)
	#~ print res
#	t = Tree(ar)
#	t.show()

"""
