#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 20:02:49 2020

@author: Mauro Leoncini, esclusivamente per scopi didattici
         Insegnamento di "Linguaggi DInamici"
         Corso di Laurea in Informatica
         Università di Modena e Reggio Emilia
         Prova di laboratorio del 19 febbraio 2020
         Turni A e B
"""

#######################################
############## Turno A ################
#######################################

import getpass   # Usata per entrambi i turni
# ATTENZIONE: getpass è incompatibile con spyder3, nel senso che
#             non è in grado di oscurare la password digitata.
#             Funziona invece se si lavora da shell
#             Con spyder, quindi, usare getpass() o input()
#             è essenzialmente la stessa cosa

class mymeta(type):
    '''
    Metaclasse per pwd_protected. Deve garantire il seguente comportamento 
    generale del "programma"
    1) Quando la classe pwd_protected viene definita deve essere richiesto
       all'utente di scegliere e digitare un'opportuna password.
    2) Ogni volta che si tenta di istanziare pwd_protected, si deve chiedere
       di digitare la password scelta, al fine di consentire la creazione
       del nuovo oggetto
    3) Se la password è errata l'oggetto non deve essere creato e deve essere
       visualizzato un opportuno messaggio di errore
    Si possono ignorare (senza alcuna penalizzazione sul voto) tutte le
    questioni di sicurezza. In particolare, le password possono
    essere visibili mentre vengono digitate
    '''
    def __init__(cls,name,bases,dictionary):
        ''' Chiede la password iniziale (due volte! naturalmente...) 
            e la memorizza in un attributo della classe pwd_protected
        '''
        while True:
            passwd = getpass.getpass(prompt='Enter a password (min 8 chars):',\
                                      stream=None)
            if len(passwd)<8:
                print("Password too short: ")
                continue
            retyped = getpass.getpass(prompt='Enter the password again:')
            if retyped != passwd:
                print("Password mismatch!")
                continue
            cls.passwd = passwd
            return
    
    def __call__(cls):
        '''
        type(cls)=mymeta e dunque __call__ viene chiamata quando
        si istanzia una classe come pwd_protected.
        '''
        passwd = getpass.getpass(prompt='Enter password: ', stream=None)
        if passwd == cls.passwd:
            return super().__call__() #equivalente a super(mymeta,cls)__call__()
        print("Password incorrect!")
        return None
        
class pwd_protected(metaclass=mymeta):
    '''
    Classe che può essere istanziata solo se in possesso di
    opportune credenziali.
    Il messaggio in __init__ deve essere visualizzato ogni volta
    che viene effettivamente creato un oggetto di tipo pwd_protected
    '''   
    def __init__(cls):
        print(f"Object {cls} created")
    
    '''
    Altre (eventuali) definizioni, non rilevanti ai fini dell'esercizio
    '''
    
def dadi(n=2,f=6):
    '''
    Simula il lancio di n dadi, ognuno con f facce numerate da 1 a f.
    Restituisce il valore totale ottenuto
    '''
    assert n>=1 and f>1
    from random import randint
    val = 0
    for _ in range(n):
        val+=randint(1,f)
    return val

def stats(n=2,f=6,numexp=1000):
    '''
    Restituisce un dizionario in cui:
    1) le chiavi sono i possibili esiti del lancio di n dadi, ciascuno 
       con f facce (numerate da 1 a f)
    2) i valori sono il corrispondente numero di volte che ogni particolare
       esito si è verificato
    numexp è il numero complessivo di lanci da simulare.
    '''
    d = {}
    for _ in range(numexp):
        v = dadi(n,f)
        d[v] = d.get(v,0)+1
    return d
        
#######################################
############## Turno B ################
#######################################    

class mymeta(type):
    '''
    Metaclasse per pwd_protected. Deve garantire il seguente comportamento 
    generale del "programma"
    1) Quando la classe pwd_protected viene definita, si genera "una password
       casuale che viene opportunamente memorizzata (e comunicata all'utente)
    2) Ogni volta che si tenta di istanziare pwd_protected, si deve chiedere
       di digitare la password scelta, al fine di consentire la creazione
       del nuovo oggetto
    3) Se la password è errata l'oggetto non deve essere creato e deve essere
       visualizzato un opportuno messaggio di errore
    Le password generate devono contenere solo cifre, lettere maiuscole e
    minuscole
    Si possono ignorare (senza alcuna penalizzazione sul voto) tutte le
    questioni di sicurezza. In particolare, le password possono
    essere visibili mentre vengono digitate
    '''    
    def __init__(cls,name,bases,dictionary):
        ''' 
        Genera una password iniziale (di 8 caratteri) e la memorizza in un 
        attributo della classe pwd_protected
        '''
        from random import randint
        from string import ascii_letters,digits
        chars = list(ascii_letters)+list(digits)
        '''
        Altro modo, meno compatto
        chars = [chr(x) for x in range(ord('0'),ord('9')+1)]+\
                [chr(x) for x in range(ord('A'),ord('Z')+1)]+\
                [chr(x) for x in range(ord('a'),ord('z')+1)]
        '''
        passwd = ''.join([chars[randint(0,len(chars)-1)] for _ in range(8)])
        cls.passwd = passwd
        print(f"The randomly generated password is: {passwd}")
    
    def __call__(cls):
        '''
        Classe che può essere istanziata solo se in possesso di
        opportune credenziali.
        Il messaggio in __init__ deve essere visualizzato ogni volta
        che viene effettivamente creato un oggetto di tipo pwd_protected
        '''
        passwd = getpass.getpass(prompt='Enter password: ', stream=None)
        if passwd == cls.passwd:
            # Alternativa a return super().__call__()
            X = cls.__new__(cls)
            X.__init__()
            return X
        print("Password incorrect!")
        return None    
        
class pwd_protected(metaclass=mymeta):
    '''
    Classe che può essere istanziata solo se in possesso di
    opportune credenziali.
    Il messaggio in __init__ deve essere visualizzato ogni volta
    che viene effettivamente creato un oggetto di tipo pwd_protected
    '''    
    def __init__(cls):
        print(f"Object {cls} created")
    
    '''
    Altre (eventuali) definizioni, non rilevanti ai fini dell'esercizio
    '''   

   
def quadratura(f,a,b,nstep=100):
    '''
    Restituisce il valore approssimato dell'area della
    regione sottostante il grafico di f fra i punti x=a e x=b
    Si suppone che f sia non negativa in tale intervallo.
    L'approssimazione viene fatta tabulando la funzione in nstep punti x_i
    di [a,b] equispaziati. La somma delle quantità ottenute
    moltiplicando i valori tabulati per l'incremento costante x_{i+1}-x_i
    fornisce l'approssimazione cercata (la più semplice, non la migliore...)
    '''
    def F(f,a,b,dx):
        x = a
        while x<b:
            v = f(x)
            x += dx
            yield v
            
    dx = (b-a)/(nstep-1)
    A = 0
    for fx in F(f,a,b,dx):
        A+=fx*dx
    return A
