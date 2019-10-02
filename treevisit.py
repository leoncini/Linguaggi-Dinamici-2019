#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 10:08:16 2019

@author: Mauro Leoncini
Simple example of a "custom iterable" class
(neither efficient nor an elegant solution...)
"""

class random_unordered_binary_tree:
    ''' Unordered binary trees (UBT) are trees whose nodes have at most 2 children,
        and these are "unordered" (i.e., there is no left or right child).
        Here UBT are representend as dictionaries: a x,y key/value pair means
        that node x has parent y. By convention, the parent of the root 
        is the root itself
        '''
    def __init__(self,n):
        self.nodes = {}
        self.height = 0
        self.root = self.__buildtree(n,0,-1)
        
    def __buildtree(self,n,counter,height):
        ''' Builds a random unordered binary tree and computes its height
        '''
        from random import randint
        assert n>0
        height += 1
        if height>self.height:
            self.height += 1
        if n > 1:
            j = randint(0,n-1)
            if j>0:
                left = self.__buildtree(j,counter,height)
                if j<n-1:
                    right = self.__buildtree(n-1-j,left,height)
                    self.nodes[left] = self.nodes[right] = counter+n
                else:
                    self.nodes[left] = counter+n
            else:
                right = self.__buildtree(n-1,counter,height)
                self.nodes[right] = counter+n
        self.nodes[counter+n] = counter+n
        return counter+n
    
    def __depth(self,x):
        ''' Return the depth of node x '''
        d = 0
        while self.nodes[x] != x:
            #print(x,self.nodes[x])
            d += 1
            x = self.nodes[x]
        return d

    def __iter__(self):
        ''' Initializes things for __next__ to properly work
        '''
        self.L = [(sorted([x for x in self.nodes.keys() if self.__depth(x) == d]),d) \
                  for d in range(self.height+1)]
        # Now self.L is a list whose elements are pairs (S,d) where S
        # is the sorted list of elements at distance d from the the root
        # Example (10 is the root, 7 and 9 are at distance 1, ....):
        # [([10], 0), ([7, 9], 1), ([3, 6, 8], 2), ([1, 2, 4, 5], 3)]
        self.next = (0,0) # next is a pair of indices into the outer and inner
                          # lists, respectively. E.g. (0,0) refers to node 10
                          # while (2,1) to node 6
        self.stopIter = False
        return self
    
    def __next__(self):
        ''' Before returning the current element and its distance,
        prepare for next iteration. This simply amounts to stepping on the
        element following the one "pointed" by next: if next=(i,j) such
        following element is (i,j+1), if j is not the last index in sublist i,
        otherwise is (i+1,0), if i is not the index of the last sublist.
        If none of the above applies, then StopIteration must occur
        '''
        if self.stopIter:
            raise StopIteration
        sindex = self.next[0] # Index of the current sublist
        eindex = self.next[1] # Index of the element in the sublist
        sublist = self.L[sindex] # The currrent sublist
        elem = sublist[0][eindex] # The element to be returned  ...
        dist = sublist[1]         # ... and its distance from the root
        # Prepare for next iteration (unless StopIteration must occur)
        if eindex == len(sublist[0])-1: # Last element in current sublist?
            if sindex == len(self.L)-1: # Last sublist?
                self.stopIter = True    # StopIteration next time
            else:
                self.next = (sindex+1,0)
        else:
            self.next = (sindex,eindex+1)
        return elem,dist