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

def getAssignment(flatten_expr):
    return flatten_expr[2:]

def isAssignment(flatten_expr):
    return flatten_expr[1] == '='

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


#test = [
#    "a = a + 1",
#    "Not(a <= 2)",
#    "a = a + 2",
#    "a < 2",
#    "9 + 2 * 3",
#    "(9 + 2) * 3",
#    "(9 + -2) * 3",
#    "(9 + -2) * 3^2^2",
#    "(9! + -2) * 3^2^2",
#    "M*X + B",
#    "M*(X + B)",
#    "1+2*-3^4*5+-+-6",
#    "(a + b)",
#    "((a + b))",
#    "(((a + b)))",
#    "((((a + b))))",
#    "((((((((((((((a + b))))))))))))))",
#]

#symbols = {'a':'a'}
#for t in test:
#    print(t)
#    a = expr.parseString(t)
#    e, symbols = parse_expr(a, symbols)
#    print(symbols)
#    print(toStr(e))
#    print("")
