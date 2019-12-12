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

#Global objects: opcodes, binary operators and list that will contain
# (possible) END statements

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

endstats = []

# Bnary operators
binops = {PLUS:'__add__',MINUS:'__sub__',MUL:'__mul__',DIV:'__rtruediv__',\
          AND:'__and__',OR:'__or__',EQ:'__eq__',NEQ:'__ne__',\
          LT:'__lt__',GT:'__gt__',LE:'__le__',GE:'__ge__'}


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
    ItInt(p[3])
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

global FT, nodenum
FT = {}
nodenum = 0

def optimize(T,continuation):
    '''Costruisce una rappresentazione ottimizzata dell'AST
       in cui ogni nodo contiene il "puntatore" al prossimo 
       nodo che deve essere visitato.
       La struttura dati utilizzata è un dizionario in cui le
       chiavi numerano i nodi e i valori sono tuple in cui 
       vengono riportate le seguenti informazioni:
           (1) la funzione del nodo, 
           (2) se il nodo corrisponde ad una foglia dell'AST,
               il suo valore lessicale, ovvero un numero o la
               stringa che corrisponde all'identificatore usato nel
               programma
           (3) il nodo successivo da visitare
        La struttura consente una visita iterativa dell'AST
        Ogni chiamata ricorsiva sulla radice T di un dato
        sottoalbero restituisce il (numero del) nodo S che deve essere
        visitato per primo in quel sottoalbero
        In input, oltre al sottoalbero T, il valore di 
        continuation è il nodo (al di fuori del sottoalbero di
        radice T) dove la computazione deve continuare in uscita
        da T. Continuation vale None per utti i nodi che "possono"
        essere gli ultimi secondo l'ordine di esecuzione.'
    '''
    global FT, nodenum
    fun = T[0]
    nodenum += 1
    this = nodenum
    if fun == SEQ:
        cont = optimize(T[2],this)
        jumpin = optimize(T[1],cont)
        FT[this] = (SEQ,continuation)
    elif fun == ASSIGN:
        jumpin = optimize(T[2],this)
        FT[this] = (ASSIGN,T[1],continuation)
    elif fun == NUMBER:
        FT[this] = (NUMBER,T[1],continuation)
        jumpin = this
    elif fun == ID:
        FT[this] = (ID,T[1],continuation)
        jumpin = this    
    elif fun in binops.keys():
        cont = optimize(T[2],this)
        jumpin = optimize(T[1],cont)
        FT[this] = (fun,continuation)
    elif fun == NOT:
        jumpin = optimize(T[1],this)
        FT[this] = (NOT, continuation)
    elif fun == UNARYMINUS:
        jumpin = optimize(T[1],this)
        FT[this] = (UNARYMINUS, continuation)
    elif fun == FUN:
        jumpin = optimize(T[2],this)
        FT[this] = (FUN, T[1], continuation)
    elif fun == PRINT:
        jumpin = optimize(T[1],this)
        FT[this] = (PRINT,continuation)
    elif fun == IF:
        jumpin = optimize(T[1],this)
        jumpif = optimize(T[2],continuation)
        FT[this] = (IF,jumpif,continuation)
    elif fun == IFELSE:
        jumpin = optimize(T[1],this)
        jumpif = optimize(T[2],continuation)
        jumpel = optimize(T[3],continuation)
        FT[this] = (IFELSE,jumpif,jumpel)
    elif fun == WHILE:
        jumpin = optimize(T[1],this)
        jumpbo = optimize(T[2],jumpin)
        FT[this] = (WHILE,jumpbo,continuation)
    return jumpin

def ItInt(ast,startnode=1):
    '''Interprete iterativo dell'AST ottimizzato. Usa uno stack
       per memorizzare gli operandi
    '''
    from collections import deque
    symbol_table = {}
    node = ast[startnode]
    # Stack: memory and primitives
    S = deque()
    push = deque.append
    pop = deque.pop
    ##############################
    while True:
        fun = node[0]
        if fun == NUMBER:
            push(S, node[1])
        elif fun == PRINT:
            print(cleanint(pop(S)))
        elif fun == NOT:
            push(S, not pop(S))
        elif fun == UNARYMINUS:
            push(S,-pop(S))
        elif fun == ID:
            try:
                push(S,symbol_table[node[1]])
            except KeyError:
                print(f"Symbol {node[1]} undefined. Aborting...")
                sys.exit()
        elif fun == ASSIGN:
            symbol_table[node[1]] = pop(S)
        elif fun == SEQ:
            pass
        elif fun == IF:
            t = pop(S)
            if t:
                node = ast[node[1]]
                continue
        elif fun == IFELSE:
            t = pop(S)
            if t:
                node = ast[node[1]]
            else:
                node = ast[node[-1]]
            continue
        elif fun == WHILE:
            t = pop(S)
            if t:
                node = ast[node[1]]
                continue
        elif fun in binops.keys():
            v1 = pop(S)
            v2 = pop(S)
            push(S, float(v2).__getattribute__(binops[fun])(v1))
        elif fun in {BEGIN,END}:
            print("BEGIN/END not yet implemented. Aborting...")
            sys.exit()
        elif fun == FUN:
            f = getattr(math,node[1])
            v = pop(S)
            push(S,f(v))
        
        if node[-1] is None:
            return
        node = ast[node[-1]]
        
def ldparser(fn=None):
    from time import time
    parser = yacc.yacc()
    if fn:
        with open(fn,'r') as program:
            s = ''.join(program.readlines())
    else:
        s = input('Type the input program: ')
    ast = parser.parse(s)
    startnode = optimize(ast,None)
    print(f"Optimezed tree: {FT}\nStart node: {startnode}")
    st=time()
    ItInt(FT, startnode=startnode)
    ft=time()
    print(f"Execution (ast interpretation) time = {ft-st}s")
    for node in endstats:
        ItInt(node)

if __name__ == '__main__':
    if len(sys.argv)<2:
        ldparser()
    else:
        fn = sys.argv[1]
        ldparser(fn)
    
    
    
    