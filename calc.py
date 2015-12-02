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
	def __init__(self, tokenname, operand = None, array = None):
		self.name = random.getrandbits(64)
		self.token = tokenname
		self.op = operand
		self.array = array

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
	r'[0a-zA-Z_][a-zA-Z0-9_]*'
	if re.match(r'^[MDCLXVI]+$',t.value):

		t.type = 'ROMAN'
	elif re.match(r'0',t.value):
		t.type = 'ROMAN'
		t.value= 'nulla'
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
lines = ' '.join([line.rstrip('\n') for line in open('code.txt_old')])
print lines


# Parsing rules

precedence = (
	('left','ASSIGN'),
	('left','INEQUALITY'),
	('left','-','+'),
	('left','*','/'),
	)


def p_expression_less(p):
	'expression : expression INEQUALITY expression'
	p[0] = Node('INEQUALITY-expression',p[2], [p[1],p[3]])

def p_expression_multy(p):
	'expression : expression SEPARATOR expression'
	if isinstance(p[1],Node):
		if p[1].token == 'ORDER-expression':
			p[1].array.append(p[3])
			p[0] = p[1]
		elif p[3].token == 'ORDER-expression':
			p[3].array.insert(0, p[1])
			p[0] = p[3]
		else:
			p[0] = Node('ORDER-expression',p[2],[p[1],p[3]])
	else:
		p[0] = Node('ORDER-expression',p[2],[p[1],p[3]])

def p_expression_endexp(p):
	'expression : expression SEPARATOR'
	p[0] = p[1]


def p_expression_binop(p):
	'''expression : expression '+' expression
				  | expression '-' expression
				  | expression '*' expression
				  | expression '/' expression'''
	p[0] = Node('binary-expression',p[2],[p[1],p[3]])

def p_expression_for(p):
	'expression : FOR LPAREN expression SEPARATOR expression SEPARATOR expression RPAREN DO expression DONE'
	p[0] = Node('for-expression','for',[p[3],p[5],p[7],p[10]])

def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	#p[0] = Node('group-expression','()', [p[2]])
	p[0] = p[2]

def p_expression_assign(p):
	'expression : expression ASSIGN expression'
	p[0] = Node('assign-expression',p[2],[p[1],p[3]])

def p_expression_roman(p):
	'expression : ROMAN'
	p[0] = Node('roman-expression','XX', [p[1]])

def p_expression_id(p):
	'expression : IDENTIFIER'
	p[0] = Node('id-expression','id',[p[1]])

def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
	else:
		print("Syntax error at EOF")

import ply.yacc as yacc
yacc.yacc()




import subprocess

res = yacc.parse(lines)

def WriteParentLine(fileH, parent, onenode, orderid = None):
	if parent != "start":
		if orderid:
			fileH.write("\t{} -> {} [label=\"{}\"]\n".format(parent, onenode.name, orderid))
		else:
			fileH.write("\t{} -> {}\n".format(parent, onenode.name))

#~ exit()
def getItem(fileH, parent, onenode, orderid = None):
	if onenode.token == 'for-expression':
		fileH.write("\t{} [label=\"FOR\"]\n".format(onenode.name))
		WriteParentLine(fileH, parent, onenode, orderid)
		for i in range(len(onenode.array)):
			getItem(fileH, onenode.name, onenode.array[i], i+1)
	elif onenode.token == 'binary-expression':
		fileH.write("\t{} [label=\"Bin: {}\"]\n".format(onenode.name,onenode.op))
		WriteParentLine(fileH, parent, onenode, orderid)
		for i in range(len(onenode.array)):
			getItem(fileH, onenode.name, onenode.array[i], i+1)
	elif onenode.token == 'assign-expression':
		fileH.write("\t{} [label=\"Assign\"]\n".format(onenode.name))
		WriteParentLine(fileH, parent, onenode, orderid)
		for i in range(len(onenode.array)):
			getItem(fileH, onenode.name, onenode.array[i], i+1)
	elif onenode.token == 'INEQUALITY-expression':
		fileH.write("\t{} [label=\"INEQUAL: {}\"]\n".format(onenode.name,onenode.op))
		WriteParentLine(fileH, parent, onenode, orderid)
		for i in range(len(onenode.array)):
			getItem(fileH, onenode.name, onenode.array[i], i+1)
	elif onenode.token == 'ORDER-expression':
		fileH.write("\t{} [label=\"GROUP\"]\n".format(onenode.name))
		WriteParentLine(fileH, parent, onenode, orderid)
		for i in range(len(onenode.array)):
			getItem(fileH, onenode.name, onenode.array[i], i+1)
	elif onenode.token == 'roman-expression':
		fileH.write("\t{} [label=\"roman: {}\"]\n".format(onenode.name,onenode.array[0]))
		WriteParentLine(fileH, parent, onenode, orderid)
	elif onenode.token == 'id-expression':
		fileH.write("\t{} [label=\"id: {}\"]\n".format(onenode.name,onenode.array[0]))
		WriteParentLine(fileH, parent, onenode, orderid)


fileH = open("graph.gv", 'w')

fileH.write("digraph G {\n")
getItem(fileH, "start", res)
fileH.write("}\n")
fileH.close()


fileN = open("file.jpg", 'w')
subprocess.call(["/usr/bin/dot", "-Tjpg", "graph.gv"],shell=False, stdout=fileN)
fileN.close()
subprocess.call(["/usr/bin/gnome-open","file.jpg"])

