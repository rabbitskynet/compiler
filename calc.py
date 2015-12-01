import sys, random, re

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
literals = "+-*/"


def t_COMMENT(t):
	r'\#\#.*\n'
	pass

def t_IDENTIFIER(t):
	r'[a-zA-Z_][a-zA-Z0-9_]*'
	if re.match(r'[VIX][VIX]*',t.value):
		t.type = reserved.get(t.value.lower(),'ROMAN')
	else:
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
	('left','ASSIGN'),
	('left','INEQUALITY'),
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

import subprocess

res = yacc.parse(lines)

print res.token


def getItem(fileH, parent, array):
	print array.token
	if array.token == 'for-expression':
		fileH.write("\t{} [label=\"FOR\"]\n".format(array.name))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		getItem(fileH, array.name, array.left)
		getItem(fileH, array.name, array.right)
		getItem(fileH, array.name, array.third)
		getItem(fileH, array.name, array.four)
	elif array.token == 'binary-expression':
		fileH.write("\t{} [label=\"Bin:{}\"]\n".format(array.name,array.op))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		#~ print array.left,array.right
		getItem(fileH, array.name, array.left)
		getItem(fileH, array.name, array.right)
	elif array.token == 'assign-expression':
		fileH.write("\t{} [label=\"Assing\"]\n".format(array.name))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		#~ print array.left,array.right
		getItem(fileH, array.name, array.left)
		getItem(fileH, array.name, array.right)
	elif array.token == 'INEQUALITY-expression':
		fileH.write("\t{} [label=\"INEQUAL:{}\"]\n".format(array.name,array.op))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		#~ print array.left,array.right
		getItem(fileH, array.name, array.left)
		getItem(fileH, array.name, array.right)
	elif array.token == 'roman-expression':
		fileH.write("\t{} [label=\"roman:{}\"]\n".format(array.name,array.left))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
	elif array.token == 'id-expression':
		fileH.write("\t{} [label=\"id:{}\"]\n".format(array.name,array.left))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
	elif array.token == 'group-expression':
		fileH.write("\t{} [label=\"Group\"]\n".format(array.name))
		if parent != "start":
			fileH.write("\t{} -> {}\n".format(parent, array.name))
		getItem(fileH, array.name, array.left)




fileH = open("graph.gv", 'w')

fileH.write("digraph G {\n")
getItem(fileH, "start", res)
fileH.write("}\n")
fileH.close()


fileN = open("file.jpg", 'w')
subprocess.call(["/usr/bin/dot", "-Tjpg", "/home/progga/compiler/graph.gv"],shell=False, stdout=fileN)
fileN.close()
subprocess.call(["/usr/bin/gnome-open","/home/progga/compiler/file.jpg"])

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
