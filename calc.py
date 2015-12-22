#!/usr/bin/env python
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
lines = ' '.join([line.rstrip('\n') for line in open('code2.txt')])
print lines


# Parsing rules

precedence = (
	('left','ASSIGN'),
	('left','INEQUALITY'),
	('left','-','+'),
	('left','*','/'),
	)


def p_expression_multy(p):
	'''expression : expression SEPARATOR expression
				  | expression SEPARATOR Assexpression
				  | Assexpression SEPARATOR expression
				  | Assexpression SEPARATOR Assexpression'''
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
	'''expression : expression SEPARATOR
				  | Assexpression SEPARATOR'''
	p[0] = p[1]

def p_expression_binop(p):
	'''expression : expression '+' expression
				  | expression '-' expression
				  | expression '*' expression
				  | expression '/' expression'''
	p[0] = Node('binary-expression',p[2],[p[1],p[3]])

def p_expression_for(p):
	'expression : FOR LPAREN Assexpression SEPARATOR InequalityExp SEPARATOR Assexpression RPAREN DO expression DONE'
	p[0] = Node('for-expression','for',[p[3],p[5],p[7],p[10]])

def p_expression_group(p):
	'expression : LPAREN expression RPAREN'
	#p[0] = Node('group-expression','()', [p[2]])
	p[0] = p[2]

def p_expression_assign(p):
	'''Assexpression : expression ASSIGN expression
				     | expression ASSIGN InequalityExp'''
	p[0] = Node('assign-expression',p[2],[p[1],p[3]])

def p_expression_less(p):
	'InequalityExp : expression INEQUALITY expression'
	p[0] = Node('INEQUALITY-expression',p[2], [p[1],p[3]])


def p_expression_id(p):
	'expression : IDENTIFIER'
	p[0] = Node('id-expression','id',[p[1]])


def p_expression_roman(p):
	'expression : ROMAN'
	p[0] = Node('roman-expression','XX', [p[1]])


def p_error(p):
	if p:
		print("Syntax error at '%s'" % p.value)
		exit()
	else:
		print("Syntax error at EOF")
		exit()

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

registers = [ 'D', 'E', 'H', 'L']
lastRegister = 0
lastifcondition = 0
lastforcondition = 0
def getNextRegister():
	global lastRegister
	ret = ""
	if lastRegister < len(registers):
		ret = registers[lastRegister]
		lastRegister+=1
	else:
		ret = registers[0]
		lastRegister=1
	return ret	


Names = {}
TotalCode={}

def getType(item, ret):
	if item is not None:
		if "value" in item:
			if re.match(r'^[MDCLXVI]+$',item['value']) or item['value'] == "nulla":
				return item['value']
			else:
				if item['value'] in Names.keys():
					return Names[item['value']]
		elif "code" in item:
			return ret
		elif "group" in item:
			return ret
	print "getType: none"
	return ret



def removeSpec(key):
	listy = ('value', 'variable', 'exitlabel')
	return key not in listy

def GetCode(onenode):
	global lastifcondition,lastforcondition 
	global Names
	if onenode.token == 'for-expression':
		#~ print "Node: FOR cycle"
		forlabel = "ifcondition_{:03d}".format(lastforcondition)

		lastforcondition+=1
		setvar = GetCode(onenode.array[0])
		res=[]
		for key in setvar.keys():
			if removeSpec(key):
				res +=setvar[key]
		res += [forlabel+":"]
		checkvar = GetCode(onenode.array[1])
		for key in checkvar.keys():
			if removeSpec(key):
				res +=checkvar[key]
		blockvar = GetCode(onenode.array[3])
		for key in blockvar.keys():
			if removeSpec(key):
				res +=blockvar[key]
		incvar = GetCode(onenode.array[2])
		for key in incvar.keys():
			if removeSpec(key):
				res +=incvar[key]
		res += ["JMP "+forlabel]
		res += [checkvar['exitlabel']+":"]
		return {'code': res }
	elif onenode.token == 'binary-expression':
		#~ print "Node: binary"
		right = GetCode(onenode.array[1])
		left = GetCode(onenode.array[0])
		res=[]
		#old#~ print ("mov Ax = "+ tmparr[0] if getType(tmparr[0]) else "C")
		#~ print left,onenode.op,right
		
		#~ print getType(left),onenode.op,getType(right)
		#~ print ("mov Ax = "+ getType(left) if getType(left) else "C")
		for key in right.keys():
			if removeSpec(key):
				res +=right[key]
		for key in left.keys():
			if removeSpec(key):
				res +=left[key]
		res += ["mov Ax = "+ getType(left,"C")]
		#~ print ["mov Ax = "+ getType(left,"C")]
		op = None
		if onenode.op == "+":
			op = "add"
		elif onenode.op == "-":
			op = "sub"
		elif onenode.op == "*":
			op = "mul"
		else:
			op = "div"
		#print ""+op+" Ax," +  getType(right) if getType(right) else "D"
		res += [""+op+" Ax," +  getType(right,"C")]
		#~ print [""+op+" Ax," +  getType(right,"C")]
		#print "mov C, Ax"
		res += ["mov C, Ax"]
		#~ print "mov C, Ax"
		return {'code': res }
	elif onenode.token == 'assign-expression':
		#~ print "Node: assign"
		right = GetCode(onenode.array[1])
		left = GetCode(onenode.array[0])
		res=[]
		for key in right:
			if removeSpec(key):
				res +=right[key]
		for key in left:
			if removeSpec(key):
				res +=left[key]
			
		res += ["mov Ax, "+ getType(right,"C")]
		res += ["mov "+ getType(left,"C")+ ", Ax"]
		return {'code': res, 'variable': getType(left,"C") }
	elif onenode.token == 'INEQUALITY-expression':
		#~ print "Node: inequality"
		right = GetCode(onenode.array[1])
		left = GetCode(onenode.array[0])
		res=[]
		for key in right:
			if removeSpec(key):
				res +=right[key]
		for key in left:
			if removeSpec(key):
				res +=left[key]
		res += ["mov Ax, "+getType(left,"C")]
		res += ["cmp Ax, "+getType(right,"C")]
		label = "exitcondition_{:03d}".format(lastifcondition)
		lastifcondition +=1
		if onenode.op == "==":
			res += ["JNE "+label]
		elif onenode.op == "<":
			res += ["JNL "+label]
		elif onenode.op == "<=":
			res += ["JNLE "+label]
		elif onenode.op == ">":
			res += ["JNG "+label]
		elif onenode.op == ">=":
			res += ["JNGE "+label]		
		return {'code': res, 'exitlabel': label }
		

	elif onenode.token == 'ORDER-expression':
		#~ print "Node: order"
		res = []
		for item in onenode.array:
			left = GetCode(item)
			for key in left:
				if removeSpec(key):
					res +=left[key]
			res +=["NOP"]
		#~ print "LEFT", left
		#~ print "RIGHT",right
		res = res[:-1]
		return {'group': res}
	elif onenode.token == 'roman-expression':
		#Dprint "Node: roman"
		#Dprint [onenode.array[0]]
		return {'value': onenode.array[0]}
	elif onenode.token == 'id-expression':
		#Dprint "Node: id"
		if onenode.array[0] not in Names:
			Names[onenode.array[0]] = getNextRegister()
			#Dprint "Node [{}] will reserve in {}".format(onenode.array[0], Names[onenode.array[0]])
			#Dprint [onenode.array[0]]
		return {'value': onenode.array[0]}	



fileH = open("graph.gv", 'w')
print
fileH.write("digraph G {\n")
getItem(fileH, "start", res)
res = GetCode(res)
for key in res:
	for line in res[key]:
		print line
fileH.write("}\n")
fileH.close()


#~ VAR1 := I+ V * II ; VAR2 := VAR1 - VX ; VAR3 := VAR1 + VAR2;
#~ for ( i := I; i < X ; i := i+I) do
	#~ VSC := VSC + i;
#~ done

fileN = open("file.jpg", 'w')
subprocess.call(["/usr/bin/dot", "-Tjpg", "graph.gv"],shell=False, stdout=fileN)
fileN.close()
subprocess.call(["/usr/bin/gnome-open","file.jpg"])

