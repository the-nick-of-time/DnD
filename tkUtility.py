"""
Tkinter Utility
Version 1.0 (released 2016-01-09)
Direct all comments, suggestions, etc. at /u/the-nick-of-time

This module contains simple functions to automate common operations done with
tkinter objects.

labeledEntry creates and places an entry and accompanying label, returning the
entry object for outside use.

replaceEntry replaces the contents of an entry with a new string.
"""

import tkinter as tk

def labeledEntry(master, name, r, c, orient='v', width=20, pos=''):
    l=tk.Label(master,text=name)
    l.grid(row=r,column=c,sticky=pos)
    e=tk.Entry(master,width=width)
    if(orient=='v'):
        e.grid(row=r+1,column=c,sticky=pos)
    elif(orient=='h'):
        e.grid(row=r,column=c+1,sticky=pos)
    return e

def replaceEntry(e, new):
    e.delete(0,'end')
    e.insert(0,new)
