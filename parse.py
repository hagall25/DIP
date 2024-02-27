#
# simpleArith.py
#
# Example of defining an arithmetic expression parser using
# the infixNotation helper method in pyparsing.
#
# Copyright 2006, by Paul McGuire
#
import sys
from pyparsing import *
import numpy
import predicate

ppc = pyparsing_common

ParserElement.enablePackrat()
sys.setrecursionlimit(3000)

integer = ppc.integer
variable = Word(alphas,alphanums + '_')
operand = integer | variable

signop = oneOf("+ -")
multop = oneOf("* /")
plusop = oneOf("+ -")
boolop = oneOf("And Or || && ,")
neqop = oneOf("Not !")
eqop = oneOf('= == <= >= < > !=')


# To use the infixNotation helper:
#   1.  Define the "atom" operand term of the grammar.
#       For this simple grammar, the smallest operand is either
#       and integer or a variable.  This will be the first argument
#       to the infixNotation method.
#   2.  Define a list of tuples for each level of operator
#       precedence.  Each tuple is of the form
#       (opExpr, numTerms, rightLeftAssoc, parseAction), where
#       - opExpr is the pyparsing expression for the operator;
#          may also be a string, which will be converted to a Literal
#       - numTerms is the number of terms for this operator (must
#          be 1 or 2)
#       - rightLeftAssoc is the indicator whether the operator is
#          right or left associative, using the pyparsing-defined
#          constants opAssoc.RIGHT and opAssoc.LEFT.
#       - parseAction is the parse action to be associated with
#          expressions matching this operator expression (the
#          parse action tuple member may be omitted)
#   3.  Call infixNotation passing the operand expression and
#       the operator precedence list, and save the returned value
#       as the generated pyparsing expression.  You can then use
#       this expression to parse input strings, or incorporate it
#       into a larger, more complex grammar.
#
expr = infixNotation(
    operand,
    [
        (neqop, 1, opAssoc.RIGHT),
        (signop, 1, opAssoc.RIGHT),
        (multop, 2, opAssoc.LEFT),
        (plusop, 2, opAssoc.LEFT),
        (boolop, 2, opAssoc.LEFT),
        (eqop, 2, opAssoc.LEFT)
    ],
)

def isPredicate(flatten):
    for atom in flatten:
        if atom == boolop:
            return True
    return False

def getAssignment(flatten_expr):
    return flatten_expr[2:]

def isAssignment(flatten_expr):
    return flatten_expr[1] == '='

def inToPos(flatten):
    l = []
    ii = 0
    for atom in flatten:
        if isinstance(atom, list):
            atom =  inToPos(atom)
            flatten[ii] = atom
        ii+=1
    while(len(flatten)>2):
        for i in range(len(flatten)-2):
            if flatten[i+1] == 'Or' or flatten[i+1] == '||':
                flatten =  flatten[:i] + ['Or'] + [[flatten[i]]  + [',']+ [inToPos(flatten[i+2:])]]
                break
        break
    return flatten


def toPrefixOr(strexpr):
    a = expr.parseString(strexpr)
    flatten = a.asList()[0]
    flatten = inToPos(flatten)
    return toStr(flatten)

#Replace all variables with values in symbols
def replaceSymbols(expression, symbols):
    for i, op in enumerate(expression):
        if type(op) is list:
            expression[i] = replaceSymbols(op, symbols)
        if op == variable and op in symbols:
            if symbols[op] != op:
                expression[i] = toStr(symbols[op])
    return expression

def toStr(expression):
    stri = ""
    for op in expression:
        if type(op) is list:
            stri+='('
            stri += toStr(op)
            stri += ')'
        else:
            stri += str(op)
            stri += ' '
        
    return stri

#Handle expressions
def parse_expr(expr, symbols):
    flatten = expr.asList()[0]
    if isAssignment(flatten):
        symbols[flatten[0]] = replaceSymbols(getAssignment(flatten), symbols)
    else:
        flatten = replaceSymbols(flatten, symbols)
    return flatten, symbols


def parse(expression, symbols):
    a = expr.parseString(expression)
    parsed, sym =  parse_expr(a, symbols)
    return toStr(parsed), sym

def symb(parsed):
    res = []
    if isinstance(parsed, str):
        if parsed == variable and parsed != boolop and parsed != neqop:
            res.append(parsed)
    elif(isinstance(parsed, list)):
        for par in parsed:
            for sym in symb(par):
                res.append(sym)
    return res

def get_symbols(expression, symbols):
    a = expr.parseString(expression)
    parsed, sym =  parse_expr(a, symbols)
    res = symb(parsed)
    return res

def make_struct(flatten):
    if isinstance(flatten, predicate.LogicalAnd) or isinstance(flatten, predicate.LogicalOr) or isinstance(flatten, predicate.LogicalNot):
        return flatten
    i = 0
    for atom in flatten:
        if atom == neqop:
            n = predicate.LogicalNot(make_struct(flatten[i+1]))
            new = flatten
            new = new[:i]
            new.append(n)
            new = new + flatten[i+2:]
            flatten = new
        i+=1
    if len(flatten) < 2:
        return flatten[0]

    
    ret = None
    while flatten[1] == boolop:
        if flatten[1] == "||":
            ret = predicate.LogicalOr(make_struct(flatten[0]), make_struct(flatten[2]))
        elif flatten[1] == "&&":
            ret = predicate.LogicalAnd(make_struct(flatten[0]), make_struct(flatten[2]))
        flatten = flatten[3:]
        flatten.insert(0, ret)
        if len(flatten) < 2:
            break
    if ret == None:
        if not isinstance(flatten, predicate.LogicalNot):
            ret = toStr(flatten)
            # for s in flatten.toStr():
            #     ret+=str(s)
        else:
            ret = flatten
    return ret

def process_predicate(predicatee, symbols):
    predicatee, s = parse(predicatee, symbols)
    a = expr.parseString(predicatee)
    flatten = a.asList()[0]
    a = make_struct(flatten)
    res = predicate.eval_combs(a)
    
    return res

def remove_or(predicatee):
    a = expr.parseString(predicatee)
    flatten = a.asList()[0]
    a = make_struct(flatten)
    res = predicate.make_formula_t(a, '')
    return res

def generate_mcdc(predicatee):
    a = expr.parseString(predicatee)
    flatten = a.asList()[0]
    a = make_struct(flatten)
    res = predicate.generate_coverage(a)
    return res

test = [
   "a = a + 1",
   "Not(a <= 2)",
   "a = a + 2",
   "a < 2",
   "9 + 2 * 3",
   "(9 + 2) * 3",
   "(9 + -2) * 3",
   "(9 + -2) * 3^2^2",
   "(9! + -2) * 3^2^2",
   "M*X + B",
   "M*(X + B)",
   "1+2*-3^4*5+-+-6",
   "(a + b)",
   "((a + b))",
   "(((a + b)))",
   "((((a + b))))",
   "((((((((((((((a + b))))))))))))))",
]

# symbols = {'a':'a'}
# for t in test:
    # print(t)
    # a = expr.parseString(t)
    # e, symbols = parse_expr(a, symbols)
    # print(symbols)
    # print(toStr(e))
    # print("")
#process_predicate("(a < b) || (a>1)")