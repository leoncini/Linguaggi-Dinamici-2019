#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 08:11:59 2019

@author: Mauro Leoncini, for teaching purposes 
                         (design based on an example in the PLY doc)
         Course info: Linguaggi dinamici
                      CdL Informatics
                      University of Modena and Reggio Emilia
"""

import ply.yacc as yacc
import sys

# Get the token map from the lexer.  This is required.
from  ldlex import tokens
import math

#Global objects: opcodes, symbol table, binary operators and list
# of END statements

# OPCODES
EMPTY = 0
NUMBER = 1
ID = 2
SEQ = 3
ASSIGN = 4
PLUS = 5
MINUS = 6
UNARYMINUS = 7
MUL = 8
DIV = 9
AND = 10
OR = 11
NOT = 12
EQ = 13
NEQ = 14
LT = 15
GT = 16
LE = 17
GE = 18
PRINT = 19
IF = 20
IFELSE = 21
WHILE = 22
BEGIN = 23
END = 24
FUN = 25

symbol_table = {}

# Bnary operators
binops = {PLUS:'__add__',MINUS:'__sub__',MUL:'__mul__',DIV:'__rtruediv__',\
          AND:'__and__',OR:'__or__',EQ:'__eq__',NEQ:'__ne__',\
          LT:'__lt__',GT:'__gt__',LE:'__le__',GE:'__ge__'}

# List of statement to be executed before the interpreter exits
# Each statement is actually the root of an AST
endstats = []

# Language grammar with associeted code to build the ASTs
def p_program_exp(p):
    'program : statement_list'
    p[0] = p[1]
    
def p_statement_list(p):
    'statement_list : statement SEP statement_list'
    p[0] = (SEQ,p[1],p[3])
    
def p_statement(p):
    'statement_list : statement'
    p[0] = p[1]
    
def p_statement_expr(p):
    'statement : expression'
    p[0] = p[1]
    
def p_statement_bool(p):
    'statement : boolexp'
    p[0] = p[1]
    
def p_statement_ass(p):
    'statement : ID ASSIGN expression'
    p[0] = (ASSIGN,p[1],p[3])
    
def p_statement_print(p):
    '''statement : PRINT LPAR expression RPAR
                 | PRINT LPAR boolexp RPAR'''
    p[0] = (PRINT, p[3])

def p_statement_if(p):
    'statement : IF boolexp LCUR statement_list RCUR'
    p[0] = (IF,p[2],p[4])
    
def p_statement_ifelse(p):
    'statement : IF boolexp LCUR statement_list RCUR ELSE LCUR statement_list RCUR'
    p[0] = (IFELSE, p[2], p[4], p[8])
    
def p_statement_while(p):
    'statement : WHILE boolexp LCUR statement_list RCUR '
    p[0] = (WHILE, p[2], p[4])

def p_statement_begin(p):
    '''statement : BEGIN LCUR statement_list RCUR'''
    interpreter(p[3])
    p[0] = (BEGIN,)
    
def p_statement_end(p):
    '''statement : END LCUR statement_list RCUR'''
    endstats.append(p[3])
    p[0] = (END,)
    
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = (PLUS, p[1], p[3])

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = (MINUS, p[1], p[3])

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term MUL factor'
    p[0] = (MUL, p[1], p[3])

def p_term_div(p):
    'term : term DIV factor'
    p[0] = (DIV, p[1], p[3])

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_id(p):
    'factor : ID'
    p[0] = (ID,p[1])

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = (NUMBER,p[1])

def p_factor_expr(p):
    'factor : LPAR expression RPAR'
    p[0] = p[2]
    
def p_factor_neg(p):
    'factor : MINUS factor'
    p[0] = (UNARYMINUS, p[2])

def p_factor_pi(p):
    'factor : PI'
    p[0] = p[1]
    
def p_factor_fun(p):
    'factor : FUN LPAR expression RPAR'
    p[0] = (FUN, p.slice[1].value, p[3])

def p_expression_or(p):
    'boolexp : boolexp OR boolterm'
    p[0] = (OR,p[1],p[3])
    
def p_expression_or_term(p):
    'boolexp : boolterm'
    p[0] = p[1]
    
def p_expression_and(p):
    'boolterm : boolterm AND boolfact'
    p[0] = (AND,p[1],p[3])

def p_expression_and_fact(p):
    'boolterm : boolfact'
    p[0] = p[1]
    
def p_expression_not(p):
    'boolfact : NOT boolfact '
    p[0] = (NOT,p[2])
    
def p_expression_eq(p):
    'boolfact : expression EQ expression '
    p[0] = (EQ,p[1],p[3])
    
def p_expression_neq(p):
    'boolfact : expression NEQ expression '
    p[0] = (NEQ,p[1],p[3])
    
def p_expression_lt(p):
    'boolfact : expression LT expression '
    p[0] = (LT,p[1],p[3])
    
def p_expression_gt(p):
    'boolfact : expression GT expression '
    p[0] = (GT,p[1],p[3])
    
def p_expression_le(p):
    'boolfact : expression LE expression '
    p[0] = (LE,p[1],p[3])
    
def p_expression_ge(p):
    'boolfact : expression GE expression '
    p[0] = (GE,p[1],p[3])

# Error rule for syntax errors
def p_error(p):
    if 'value' in dir(p): # p is a lextoken
        print("Syntax error in input!")
    else:                 # p is an ID
        print(f"{p[1]} undefined")


def cleanint(x):
    '''If x (which is of type float) represents and integer,
       return the same value as an int
    '''
    if x==int(x):
        return int(x)
    else:
        return x

def interpreter(ast):
    '''Visits (in postorder) the tree built by the compiler and 
       executes the opcodes
    '''
    fun = ast[0]
    if fun == NUMBER:
        return cleanint(ast[1])
    elif fun == PRINT:
        print(cleanint(interpreter(ast[1])))
    elif fun == NOT:
        return not interpreter(ast[1])
    elif fun == UNARYMINUS:
        return -interpreter(ast[1])
    elif fun == ID:
        try:
            return symbol_table[ast[1]]
        except KeyError:
            print(f"Symbol {ast[1]} undefined. Aborting...")
            sys.exit()
    elif fun == ASSIGN:
        symbol_table[ast[1]] = interpreter(ast[2])
    elif fun == SEQ:
        interpreter(ast[1])
        interpreter(ast[2])
    elif fun == IF:
        if interpreter(ast[1]):
            interpreter(ast[2])
    elif fun == IFELSE:
        if interpreter(ast[1]):
            interpreter(ast[2])
        else:
            interpreter(ast[3])
    elif fun == WHILE:
        while interpreter(ast[1]):
            interpreter(ast[2])
    elif fun in binops.keys():
        arg1 = interpreter(ast[1])
        arg2 = interpreter(ast[2])
        return float(arg1).__getattribute__(binops[fun])(arg2)
    elif fun in {BEGIN,END}:
        return
    elif fun == FUN:
        f = getattr(math,ast[1])
        return f(interpreter(ast[2]))
    else: # must not happen
        print(f"Undefined opcode {fun}. Aborting...")
        sys.exit()
      
def exp_parser(fn=None):
    from time import time
    parser = yacc.yacc()
    if fn:
        with open(fn,'r') as program:
            s = ''.join(program.readlines())
    else:
        s = input('Type the input program: ')
    ast = parser.parse(s)
    #print(ast)
    st=time()
    interpreter(ast)
    ft=time()
    print(f"Execution (ast interpretation) time = {ft-st}s")
    for t in endstats:
        interpreter(t)

if __name__ == '__main__':
    if len(sys.argv)<2:
        exp_parser()
    else:
        fn = sys.argv[1]
        exp_parser(fn)
