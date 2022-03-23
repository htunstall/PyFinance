# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 23:30:32 2022

@author: Harry
"""
import time
import tkinter
import calendar
from   datetime             import datetime
from   tkinter              import ttk
from   tkinter.font         import Font
from   tkinter.scrolledtext import ScrolledText

import database
import lookup


#------------------------------------------------------------------------------
# Global Variables
#------------------------------------------------------------------------------
min_width = 690 # Std: 650
min_height = 500
xpad = 3
ixpad = 2
ypad = 4
iypad= 2

history = 10 # How many previous values should we show
#------------------------------------------------------------------------------
def log(logbox, message, blank=False, append=None, colour="black", tag_number=0, font="normal", underline=False, show_time=False):
    """
    This procedure writes the message to the log box, with various controlable options,
      for example, the append feild can append font of a different colour to the same line.
      
    Variable list:
        logbox:      The object that is the ScrolledText widget
        message:     A text string message
        blank:       If True, then then a blank line is printed to the ScrolledText
        append:      If this is not None, then this text string is appended to the end of the
                        message string. The font colour is determined by the colour variable,
                        and if underline is True the appended text is underlined.
        colour:      The colour of the appended text
        tag_number:  This is a unique ID for the appended text, if two IDs match then the
                        formating of the appended strings will be the same
        font:        Is the appended text "normal", "bold" etc.
        underline:   Controls the underline of the appended text
        show_time:   If True, the time will be prepended to the message like so "(HH:MM) "
    """
    _user_message = None
    _size = 10
    d_font = Font(family='Consolas', size=_size)
    if not blank:
        if show_time:
            _user_message = "({}) {}".format(time.strftime("%H:%M"), message)
        else:
            _user_message = message
    else:
        _user_message = ""
    
    if font == "bold":
        font = Font(family='Consolas', weight="bold", size=_size)
    else:
        font = d_font
    
    # Make the logbox editable
    logbox.config(state="normal")    
    # Add some text
    tag = "{0}".format(tag_number)
    if append != None:        
        logbox.insert("end", _user_message,  "default")
        logbox.insert("end", str(append) + "\n", tag)
    else:
        logbox.insert("end", _user_message + "\n", tag)
        
    logbox.tag_config(tag, foreground=colour, underline=underline, font=font)    
    logbox.tag_config("default", foreground="black", font=d_font)
    # Scroll to the end and make the box uneditable
    logbox.see("end")
    logbox.config(state="disabled")
#------------------------------------------------------------------------------

def wipeLog(logbox, start_i="1.0", end_i=tkinter.END):
    """
    Clear the ScrolledText logbox.
    """
    logbox.config(state="normal")
    logbox.delete(start_i, end_i)
    logbox.config(state="disabled")
#------------------------------------------------------------------------------

def enterExpense():
    #--------------------------------------------------------------------------
    # Load the database
    #--------------------------------------------------------------------------
    expenses = database.openCollection()
    
    # Set procedure variables
    dp = 3 # Decimal places
    
    def update_courtney(*args):
        courtney.set(round(fraction.get() * amount.get(), dp))
    
    
    def update_fraction(*args):
        if amount.get() != 0:
            fraction.set(round(courtney.get() / amount.get(), dp))
        else:
            fraction.set(0.5)
           
            
    def log_document(doc):
        # Work out the sinage
        if doc["Amount"] < 0:
            sign = "-"
            amount_val   = -doc["Amount"]
            courtney_val = -doc["Courtney"]
        else:
            sign = " "
            amount_val   = doc["Amount"]
            courtney_val = doc["Courtney"]
        
        format_str   = "{:<60} | {:<10s} | {:^8s} | {}£{:>6.2f} | {:8.3f} | {}£{:7.3f}".format(doc["Name"], doc["Date"].strftime("%d-%b-%y"), doc["Category"], sign, amount_val, fraction.get(), sign, courtney_val)
        
        log(logbox, format_str)
        
    
    def submit_expense(expenses):
        # Validation: Is the Category in the list, and is the day valid
        max_day = calendar.monthrange(year.get(), lookup.month_str_to_number[month.get().lower()])[1]
        if day.get() < 1 or day.get() > max_day:
            tkinter.messagebox.showwarning("Warning!", "The entered calendar date is not valid")
            return
           
        if category.get().upper() not in lookup.valid_categories:
            tkinter.messagebox.showwarning("Warning!", "The entered category is not valid")
            return
        
        if name.get() == "":
            tkinter.messagebox.showwarning("Warning!", "The name must be a nonzero length string")
            return
            
        doc = {"Name"      : name.get(),
               "Date"      : datetime(year.get(), lookup.month_str_to_number[month.get().lower()], day.get()),
               "Category"  : category.get().upper(),
               "Amount"    : amount.get(),
               "Courtney"  : courtney.get(),
               "Recurring" : recurring.get()}
        
        
        # Submit document to database
        expenses.insert_one(doc)
        
        # Update the most recent enteries   
        log_document(doc)
        
        # Reset the values
        name.set("")
        amount.set(0.0)
        fraction.set(0.5)
        courtney.set(0.0)
        
    def remove_last_expense(expenses):
        # _id include date submitted, hence able to retreive the last item
        doc = list(expenses.find().sort("_id", -1).limit(1))[0]
        expenses.delete_one({"_id" : doc["_id"]})
        
        # Remove it from the logbox        
        wipeLog(logbox, "end-2l", "end-1l")

    
    #--------------------------------------------------------------------------
    # Variables
    #--------------------------------------------------------------------------
    current_date = datetime.now()
    name         = tkinter.StringVar()
    day          = tkinter.IntVar(value=1)
    month        = tkinter.StringVar(value=current_date.strftime("%b"))
    year         = tkinter.IntVar(value=current_date.year)
    category     = tkinter.StringVar()
    amount       = tkinter.DoubleVar()
    fraction     = tkinter.DoubleVar(value=0.5)
    courtney     = tkinter.DoubleVar()
    recurring    = tkinter.BooleanVar(value=False)
    #--------------------------------------------------------------------------
    
    expense_window = tkinter.Toplevel()
    expense_window.title("Expense")
    expense_window.minsize(width=min_width, height=min_height)
    expense_window.resizable(width=True, height=True)
    
    #--------------------------------------------------------------------------
    # Month/Year Selection
    #--------------------------------------------------------------------------
    month_frame = tkinter.LabelFrame(expense_window, text="Month")
    month_w     = ttk.Combobox(month_frame, values=lookup.months_list, textvariable=month, width=5)
    year_w      = ttk.Entry(month_frame, textvariable=year, width=5)
    month_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    month_w.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    year_w.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    
    #--------------------------------------------------------------------------
    # Previous Values Log
    #--------------------------------------------------------------------------
    log_frame = tkinter.LabelFrame(expense_window, text="Previous Values")
    
    # ScrolledText log box
    logbox = ScrolledText(log_frame, undo=True, borderwidth=3, wrap="word", width=110, state="disabled")
    logbox.pack(fill="both", expand=1, side="top", padx=xpad, pady=ypad)
    
    #--------------------------------------------------------------------------
    # The Expense Frame
    #--------------------------------------------------------------------------
    expense_values = tkinter.LabelFrame(expense_window, text="Itemised Expense")
    expense_values.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # The fields
    # Name
    name_text = tkinter.Label(expense_values, text="Name")
    name_w    = tkinter.Entry(expense_values, textvariable=name, width=70)
    
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
    recc_w    = tkinter.Checkbutton(expense_values, variable=recurring, onvalue=True, offvalue=False)
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
    submit_bt = tkinter.Button(expense_values, text="Submit", command=lambda:submit_expense(expenses))
    submit_bt.grid(row=1, column=9, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # Undo button
    undo_bt = tkinter.Button(expense_values, text="Undo", command=lambda:remove_last_expense(expenses))
    undo_bt.grid(row=1, column=10, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # Pack the log frame
    log_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Fill the log frame
    #--------------------------------------------------------------------------
    # Header
    header       = "{:<60} | {:<10s} | {:<8s} | {:<8s} | {:<8s} | {:<9s}".format("Name of Expense", "Date", "Category", "Amount", "Fraction", "Courtney")
    row          = "-" * len(header)
    
    log(logbox, header)
    log(logbox, row)

    #--------------------------------------------------------------------------
    # Initial Enteries
    #--------------------------------------------------------------------------
    # Find last date entered, if "# documents < history" list all dates until history length is reached
    last_docs = expenses.find().sort("Date", -1).limit(history)
    dates = list(set([doc["Date"] for doc in last_docs]))

    for doc in expenses.find({"Date" : {"$in" : dates}}).sort("Date", 1):
        log_document(doc)

    
    
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