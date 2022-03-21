# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 23:30:32 2022

@author: Harry
"""

import tkinter
from   tkinter              import ttk

from   tkinter.scrolledtext import ScrolledText

months_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

#------------------------------------------------------------------------------
# Global Variables
#------------------------------------------------------------------------------
min_width = 690 # Std: 650
min_height = 500
xpad = 3
ixpad = 2
ypad = 4
iypad= 2

history = 5 # How many previous values should we show
#------------------------------------------------------------------------------

def enterExpense():
    def update_courtney(*args):
        courtney.set(fraction.get() * amount.get())
    
    def update_fraction(*args):
        if amount.get() != 0:
            fraction.set(courtney.get() / amount.get())
        else:
            fraction.set(0.5)
            
            
    def submit_expense():
        # Submit the values after validation
        # Is the Category in the list?
        
        
        # Reset the values
        name.set("")
        amount.set(0.0)
        fraction.set(0.5)
        courtney.set(0.0)
        
        
    #--------------------------------------------------------------------------
    # Variables
    #--------------------------------------------------------------------------
    name      = tkinter.StringVar()
    day       = tkinter.IntVar(value=1)
    month     = tkinter.StringVar() # Auto pick this months month
    category  = tkinter.StringVar()
    amount    = tkinter.DoubleVar()
    fraction  = tkinter.DoubleVar(value=0.5)
    courtney  = tkinter.DoubleVar()
    reccuring = tkinter.BooleanVar(value=False)
    #--------------------------------------------------------------------------
    
    expense_window = tkinter.Toplevel()
    expense_window.title("Expense")
    expense_window.minsize(width=min_width, height=min_height)
    expense_window.resizable(width=True, height=True)
    
    #--------------------------------------------------------------------------
    # Month Selection
    #--------------------------------------------------------------------------
    month_frame = tkinter.LabelFrame(expense_window, text="Month")
    month_w     = ttk.Combobox(month_frame, values=months_list, textvariable=month, width=10)
    month_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    month_w.pack(side="top", anchor="nw", padx=xpad, ipadx=ixpad)
    
    #--------------------------------------------------------------------------
    # The Expense Frame
    #--------------------------------------------------------------------------
    expense_values = tkinter.LabelFrame(expense_window, text="Itemised Expense")
    expense_values.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # The fields
    # Name
    name_text = tkinter.Label(expense_values, text="Name")
    name_w    = tkinter.Entry(expense_values, textvariable=name, width=30)
    
    # Date
    # Day (int)
    day_text = tkinter.Label(expense_values, text="Day")
    day_w    = tkinter.Entry(expense_values, textvariable=day, width=5)
    
    # Category
    cat_text = tkinter.Label(expense_values, text="Category")
    cat_w    = tkinter.Entry(expense_values, textvariable=category, width=10)    
    
    # Amount
    amount_text = tkinter.Label(expense_values, text="Amount")
    pound_text  = tkinter.Label(expense_values, text="£")
    amount_w    = tkinter.Entry(expense_values, textvariable=amount, width=10)
    
    # Courtney
    # fraction
    frac_text = tkinter.Label(expense_values, text="Fraction")
    frac_w    = tkinter.Entry(expense_values, textvariable=fraction, width=7)   
    
    # value
    courtney_text   = tkinter.Label(expense_values, text="Courtney")
    courtpound_text = tkinter.Label(expense_values, text="£")
    courtney_w      = tkinter.Entry(expense_values, textvariable=courtney, width=10)
    
    
    # Reccuring
    recc_text = tkinter.Label(expense_values, text="Reccuring?")
    recc_w    = tkinter.Checkbutton(expense_values, variable=reccuring, onvalue=True, offvalue=False)
    # Default to off
    recc_w.deselect()
    
    
    name_text.grid(    row=0, column=0, sticky="w", padx=xpad, ipadx=ixpad)
    day_text.grid(     row=0, column=1, sticky="w", padx=xpad, ipadx=ixpad)
    cat_text.grid(     row=0, column=2, sticky="w", padx=xpad, ipadx=ixpad)
    amount_text.grid(  row=0, column=3, sticky="w", padx=xpad, ipadx=ixpad, columnspan=2)
    frac_text.grid(    row=0, column=5, sticky="w", padx=xpad, ipadx=ixpad)
    courtney_text.grid(row=0, column=6, sticky="w", padx=xpad, ipadx=ixpad, columnspan=2)
    recc_text.grid(    row=0, column=8, sticky="w", padx=xpad, ipadx=ixpad)
    
    name_w.grid(         row=1, column=0, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    day_w.grid(          row=1, column=1, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    cat_w.grid(          row=1, column=2, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    pound_text.grid(     row=1, column=3,            pady=ypad,             ipady=iypad)
    amount_w.grid(       row=1, column=4, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    frac_w.grid(         row=1, column=5, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    courtpound_text.grid(row=1, column=6,            pady=ypad,             ipady=iypad)
    courtney_w.grid(     row=1, column=7, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    recc_w.grid(         row=1, column=8, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Updates as we modify
    #--------------------------------------------------------------------------
    amount_w.bind(  "<FocusOut>", update_courtney)
    frac_w.bind(    "<FocusOut>", update_courtney)
    courtney_w.bind("<FocusOut>", update_fraction)
    
    # Enter value
    submit_bt = tkinter.Button(expense_values, text="Submit", command=submit_expense)
    submit_bt.grid(row=1, column=9, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Previous Values
    #--------------------------------------------------------------------------
    prev_frame = tkinter.LabelFrame(expense_window, text="Previous Values")
    prev_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # ScrolledText log box
    logbox = ScrolledText(prev_frame, undo=True, borderwidth=3, wrap="word", state="disabled")
    logbox.pack(fill="both", expand=1, side="top", padx=xpad, pady=ypad)
    
#------------------------------------------------------------------------------


top = tkinter.Tk()

top.title("PyFinance")
top.minsize(width=min_width, height=min_height)
top.resizable(width=True, height=True)

# Buttons
master_buttons = tkinter.LabelFrame(top, text="Operations")
master_buttons.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)

enter_bt = tkinter.Button(master_buttons, text="Enter Expense", command=enterExpense)
enter_bt.pack(side="left", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)




top.mainloop()