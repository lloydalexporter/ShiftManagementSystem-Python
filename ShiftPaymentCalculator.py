#!/usr/bin/python

import tkinter


top = tkinter.Tk()

# Code to add widgets will go here...
top.mainloop()






"""
TKinter GUI

Button / Area to drag the CSV where it will import/update the new info.
[Days are the headers in the CSV]
Then for every cell, get the: Date | Time Start | Time End | Calculated Hours (Minus 30Minute Break).

Month View:
Shows one month at a time in a big table.
Next to every week row, show the total for that week (total hours, shift count)

Calculates between the payment cutoff days (14th) and says the expected amount on the 28th.


Saves data to .DB?

Graph, monthly comparisons, shift count, 30mins break, any days that are differently scheduled? (not 10.30am-5pm)


If a data was recorded before, but no longer there, what should it do? Ask if this is correct? 


Output to make file that can be run by Siri Shortcut, to add the data to my Calendar. (Using Shortcuts terminal commands?)
"""
