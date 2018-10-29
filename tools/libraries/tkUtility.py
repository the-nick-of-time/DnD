import tkinter as tk


def labeled_entry(master, name, r, c, orient='v', width=20, pos=''):
    l = tk.Label(master, text=name)
    l.grid(row=r, column=c, sticky=pos)
    e = tk.Entry(master, width=width)
    if orient == 'v':
        e.grid(row=r + 1, column=c, sticky=pos)
    elif orient == 'h':
        e.grid(row=r, column=c + 1, sticky=pos)
    return e


def replace_entry(e, new):
    e.delete(0, 'end')
    e.insert(0, new)
