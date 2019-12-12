#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 08:11:59 2019

@author: Mauro Leoncini, for teaching purposes 
                         (design based on an example in the PLY doc)
         Course info: Linguaggi dinamici
                      CdL Informatics
                      University of Modena and Reggio Emilia
"""

import ply.lex as lex
import math

def onevarfun():
    from inspect import signature
    funtype = type(math.sqrt)
    fnames = []
    for f in dir(math):
        try:
            fun = getattr(math,f)
        except AttributeError:
            continue
        if type(fun) == funtype:
            try:
                sig = signature(fun)
                if len(sig.parameters)==1:
                    fnames.append(f)
            except ValueError:
                continue
    return fnames

reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while': 'WHILE',
    'BEGIN' : 'BEGIN',
    'END': 'END'
}

tokens = [
    'ID',
    'NUMBER',
    'PLUS',
    'MINUS',
    'MUL',
    'DIV',
    'AND',
    'OR',
    'NOT',
    'LPAR',
    'RPAR',
    'LCUR',
    'RCUR',
    'SEP',
    'EQ',
    'NEQ',
    'LT',
    'GT',
    'LE',
    'GE',
    'ASSIGN',
    'PRINT',
    'PI',
    'FUN'
] + list(reserved.values()) 

t_PLUS  = r'\+'
t_MINUS = r'-'
t_MUL   = r'\*'
t_DIV   = r'/'
t_LPAR  = r'\('
t_RPAR  = r'\)'
t_LCUR  = r'\{'
t_RCUR  = r'\}'
t_ASSIGN = r'='
t_SEP = r';'
t_LT = r'<';
t_GT = r'>';

def t_AND(t):
    r'and\b'
    return t

def t_OR(t):
    r'or\b'
    return t

def t_NOT(t):
    r'not\b'
    return t

def t_PRINT(t):
    r'print\b'
    return t

def t_PI(t):
    r'pi\b'
    return t

def t_EQ(t):
    r'=='
    return t

def t_NEQ(t):
    r'!='
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    if t.value in onevarfun():
        t.type = 'FUN'
    else:
        t.type = reserved.get(t.value,'ID')  # Controllo su parola chiave
    return t

# Riconosce interi e float nella notazione in virgola fissa
# Al momento è esclusa la virgola mobile
def t_NUMBER(t):
    r'\d*\.\d+|\d+'
    v = float(t.value)
    if v == int(v):
        t.value = int(v)    
    else:
        t.value = v
    return t

t_ignore  = ' \t\n'

def t_error(t):
     print("Illegal character '%s'" % t.value[0])
     t.lexer.skip(1)

lexer = lex.lex()