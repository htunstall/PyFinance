"""
Here all the code for creating the GUIs is located, and how the main brunt of
the software works together.
"""

import os
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
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
min_width  = 750  # Std: 650
min_height = 500
xpad       = 3
ixpad      = 2
ypad       = 4
iypad      = 2
history    = 10   # How many previous values should we show
#------------------------------------------------------------------------------

def log(logbox, message, blank=False, append=None, colour="black", tag_number=0, font="normal", underline=False, show_time=False):
    """
    This procedure writes the message to the log box, with various controlable
    options, for example, the append feild can append font of a different
    colour to the same line.
      
      
    Parameters
    ----------
    logbox : ScrolledText widget object
        The object that is the ScrolledText widget.
        
    message : String
        The message to qrite to the log box.

    blank : Boolean, optional
        If True, then then a blank line is printed to the ScrolledText. The 
        default is Flase.
    
    append : String, optional
        If this is not None, then this text string is appended to the end of
        the message string. The font colour is determined by the colour
        variable, and if underline is True the appended text is underlined.
        The default is None.
    
    colour : String, optional
        The colour of the appended text. The default is "black".
        
    tag_number : Integer, optional
        This is a unique ID for the appended text, if two IDs match then the
        formating of the appended strings will be the same. The default is 0.
        
    font : String. optional
        Is the appended text "normal", "bold" etc. The default is "normal".
        
    underline : Boolean, optional
        Controls the underline of the appended text. The default is False.
        
    show_time : Boolean, optional
        If True, the time will be prepended to the message like so "(HH:MM) ".
        The default is False.
    
    Returns
    -------
    None
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
    
    Parameters
    ----------
    logbox : ScrolledText widget object
        The object that is the ScrolledText widget.
        
    start_i : String, optional
        A tkinter index for the location of the cursor in the ScrolledText
        wdidget. The default is "1.0".
        
    end_i : String, optional
        A tkinter index for the location of the cursor in the ScrolledText
        wdidget. The default is tkinter.END.

    Returns
    -------
    None
    """
    logbox.config(state="normal")
    logbox.delete(start_i, end_i)
    logbox.config(state="disabled")
#------------------------------------------------------------------------------

def logDocument(logbox, doc):
    # Work out the sinage
    if doc["Amount"] < 0:
        sign = "-"
        amount_val   = -doc["Amount"]
        courtney_val = -doc["Courtney"]
    else:
        sign = " "
        amount_val   = doc["Amount"]
        courtney_val = doc["Courtney"]
        
    if doc["Recurring"]:
        rec = "Yes"
    else:
        rec = "No"
    
    format_str   = "{:<60} | {:<10s} | {:^8s} | {}£{:>8.2f} | {}£{:8.2f} | {:10s}".format(doc["Name"], doc["Date"].strftime("%d-%b-%y"), doc["Category"], sign, amount_val, sign, courtney_val, rec)
    
    log(logbox, format_str)
#--------------------------------------------------------------------------

def logHeader(logbox):
    header = "{:<60} | {:<10s} | {:<8s} | {:<10s} | {:<10s} | {:<10s}".format("Name of Expense", "Date", "Category", "Amount", "Courtney", "Recurring")
    row    = "-" * len(header)

    log(logbox, header)
    log(logbox, row)
#-------------------------------------------------------------------------- 

def expenseEntryFields(frame, collection, year, month, logbox=None, submit=True, row=0, default_name="", default_day=1, default_category="", default_amount=0, default_courtney=0, default_recurring=False):
    """
    Create the expense data entry row

    Parameters
    ----------
    frame : tkinter frame object
        what are we packing the enteries into.
    submit : Boolean, optional
        Are we drawing the submit, undo clear buttons on this row. The 
        default is True.
    row : integer, optional
        What row are the widgets drawn in. The default is 0.

    Returns
    -------
    name, day, category, amount, courtney, recurring. All tkinter 
    variables.

    """
    if logbox is None:
        submit = False
        
    dp       = 3 # Decimal places
    #--------------------------------------------------------------------------
    # Tkinter Variables
    #--------------------------------------------------------------------------
    default_fraction = 0.5
    if default_amount != 0:
        if default_courtney != 0:
            default_fraction = default_courtney / default_amount
        else:
            default_fraction = 0
    
    name         = tkinter.StringVar( value = default_name)
    day          = tkinter.IntVar(    value = default_day)
    category     = tkinter.StringVar( value = default_category)
    amount       = tkinter.DoubleVar( value = default_amount)
    fraction     = tkinter.DoubleVar( value = default_fraction)
    courtney     = tkinter.DoubleVar( value = default_courtney)
    recurring    = tkinter.BooleanVar(value = default_recurring)       
    #--------------------------------------------------------------------------
    
    def update_courtney(*args):
        courtney.set(round(fraction.get() * amount.get(), dp))
    #--------------------------------------------------------------------------
    
    def update_fraction(*args):
        if amount.get() != 0:
            fraction.set(round(courtney.get() / amount.get(), dp))
        else:
            fraction.set(0.5)
    #--------------------------------------------------------------------------
       
    def submit_expense(expenses):
        # Validation: Is the Category in the list, and is the day valid
        max_day = calendar.monthrange(year.get(), lookup.month_str_to_number[month.get().lower()])[1]
        if day.get() < 1 or day.get() > max_day:
            tkinter.messagebox.showwarning("Warning!", "The entered calendar date is not valid")
            return
           
        if category.get().upper() not in lookup.valid_categories:
            tkinter.messagebox.showwarning("Warning!", "The entered category is not valid")
            cat_w.focus_force()
            return
        
        if name.get() == "":
            tkinter.messagebox.showwarning("Warning!", "The name must be a nonzero length string")
            name_w.focus_force()
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
        logDocument(logbox, doc)
        
        # Reset the values
        name.set("")
        amount.set(0.0)
        fraction.set(0.5)
        courtney.set(0.0)
        
        # Move the focus back to the name field
        name_w.focus_set()
    #--------------------------------------------------------------------------    
        
    def remove_last_expense(expenses):
        # _id include date submitted, hence able to retreive the last item
        doc = list(expenses.find().sort("_id", -1).limit(1))[0]
        expenses.delete_one({"_id" : doc["_id"]})
        
        # Remove it from the logbox        
        wipeLog(logbox, "end-2l", "end-1l")
    #--------------------------------------------------------------------------
    
    def clear_log():
        wipeLog(logbox)
        logHeader(logbox)
    #--------------------------------------------------------------------------
    
    # The fields
    # Name
    name_text = tkinter.Label(frame, text="Name")
    name_w    = tkinter.Entry(frame, textvariable=name, width=70)
    
    # Date
    # Day (int)
    day_text = tkinter.Label(frame, text="Day")
    day_w    = tkinter.Entry(frame, textvariable=day, width=5)
    
    # Category
    cat_text = tkinter.Label(frame, text="Category")
    cat_w    = tkinter.Entry(frame, textvariable=category, width=10)    
    
    # Amount
    amount_text = tkinter.Label(frame, text="Amount")
    pound_text  = tkinter.Label(frame, text="£")
    amount_w    = tkinter.Entry(frame, textvariable=amount, width=10)
    
    # Courtney
    # fraction
    frac_text = tkinter.Label(frame, text="Fraction")
    frac_w    = tkinter.Entry(frame, textvariable=fraction, width=7)   
    
    # value
    courtney_text   = tkinter.Label(frame, text="Courtney")
    courtpound_text = tkinter.Label(frame, text="£")
    courtney_w      = tkinter.Entry(frame, textvariable=courtney, width=10)
        
    # Reccuring
    rec_text = tkinter.Label(frame, text="Reccuring?")
    rec_w    = tkinter.Checkbutton(frame, variable=recurring, onvalue=True, offvalue=False)
    
    
    name_text.grid(    row=0+row, column=0, sticky="w", padx=xpad, ipadx=ixpad)
    day_text.grid(     row=0+row, column=1, sticky="w", padx=xpad, ipadx=ixpad)
    cat_text.grid(     row=0+row, column=2, sticky="w", padx=xpad, ipadx=ixpad)
    amount_text.grid(  row=0+row, column=3, sticky="w", padx=xpad, ipadx=ixpad, columnspan=2)
    frac_text.grid(    row=0+row, column=5, sticky="w", padx=xpad, ipadx=ixpad)
    courtney_text.grid(row=0+row, column=6, sticky="w", padx=xpad, ipadx=ixpad, columnspan=2)
    rec_text.grid(     row=0+row, column=8, sticky="w", padx=xpad, ipadx=ixpad)
    
    name_w.grid(         row=1+row, column=0, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    day_w.grid(          row=1+row, column=1, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    cat_w.grid(          row=1+row, column=2, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    pound_text.grid(     row=1+row, column=3,            pady=ypad,             ipady=iypad)
    amount_w.grid(       row=1+row, column=4, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    frac_w.grid(         row=1+row, column=5, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    courtpound_text.grid(row=1+row, column=6,            pady=ypad,             ipady=iypad)
    courtney_w.grid(     row=1+row, column=7, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    rec_w.grid(          row=1+row, column=8, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Updates as we modify
    #--------------------------------------------------------------------------
    amount_w.bind(  "<FocusOut>", update_courtney)
    frac_w.bind(    "<FocusOut>", update_courtney)
    courtney_w.bind("<FocusOut>", update_fraction)
    
    if submit:
        # Enter value
        submit_bt = tkinter.Button(frame, text="Submit", command=lambda:submit_expense(collection))
        submit_bt.grid(row=1, column=9, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
        
        # Undo button
        undo_bt = tkinter.Button(frame, text="Undo", command=lambda:remove_last_expense(collection))
        undo_bt.grid(row=1, column=10, padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
        
        # Clear Log button
        clear_bt = tkinter.Button(frame, text="Clear Log", command=clear_log)
        clear_bt.grid(row=2, column=9, columnspan=2, sticky="nesw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)

    # Move the focus back to the name field
    name_w.focus_force()

    return name, day, category, amount, courtney, recurring
#------------------------------------------------------------------------------

def enterExpense():
    """
    This is the procedure that defines the GUI for entering new expenses into 
    the database. It contains sub-procedures to complete all of the necessary
    actions.

    Returns
    -------
    None.

    """
    #--------------------------------------------------------------------------
    # Load the database
    #--------------------------------------------------------------------------
    expenses = database.openCollection()

    #--------------------------------------------------------------------------
    # Tkinter Variables
    #--------------------------------------------------------------------------
    current_date = datetime.now()
    month        = tkinter.StringVar(value=current_date.strftime("%b"))
    year         = tkinter.IntVar(value=current_date.year)
    #--------------------------------------------------------------------------
    
    expense_window = tkinter.Toplevel()
    expense_window.focus_set()
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
    
    
    name, day, category, amount, courtney, recurring = expenseEntryFields(expense_values, expenses, year, month, logbox)
    

    
    # Pack the log frame
    log_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Fill the log frame
    #--------------------------------------------------------------------------
    # Header
    logHeader(logbox)

    #--------------------------------------------------------------------------
    # Initial Enteries
    #--------------------------------------------------------------------------
    # Find last date entered, if "# documents < history" list all dates until history length is reached
    last_docs = expenses.find({"Recurring" : False}).sort("Date", -1).limit(history)
    dates = list(set([doc["Date"] for doc in last_docs]))

    for doc in expenses.find({"Date" : {"$in" : dates}, "Recurring" : False}).sort("Date", 1):
        logDocument(logbox, doc)
#------------------------------------------------------------------------------

def enterRecurringExpenses():
    def add_recurring_expense(frame, names, days, categories, amounts, courtneys, recurrings):
        row = frame.grid_size()[1]
        name, day, category, amount, courtney, recurring = expenseEntryFields(expense_values, expenses, year, month, row=row, submit=False, default_recurring=True)
        
        # Append to each list
        names.append(name)
        days.append(day)
        categories.append(category)
        amounts.append(amount)
        courtneys.append(courtney)
        recurrings.append(recurring)
        
    def remove_recurring_expense(frame, names, days, categories, amounts, courtneys, recurrings):
        # remove from screen:
        max_row = frame.grid_size()[1] - 3
        for label in frame.grid_slaves():
            if int(label.grid_info()["row"]) > max_row:
                label.grid_remove()
        
        # Pop from each list
        names.pop()
        days.pop()
        categories.pop()
        amounts.pop()
        courtneys.pop()
        recurrings.pop()
        
    def submit_expenses(expenses, frame, names, year, month, days, categories, amounts, courtneys, recurrings):
        max_day = calendar.monthrange(year.get(), lookup.month_str_to_number[month.get().lower()])[1]
        for i, (name, day, category, amount, courtney, recurring) in enumerate(zip(names, days, categories, amounts, courtneys, recurrings)):
            # Validation: Is the Category in the list, and is the day valid
            if day.get() < 1 or day.get() > max_day:
                tkinter.messagebox.showwarning("Warning!", "The entered calendar date `{}` on row {} is not valid".format(day.get(), i+1))
                frame.focus_force()
                return
               
            if category.get().upper() not in lookup.valid_categories:
                tkinter.messagebox.showwarning("Warning!", "The entered category `{}` on row {} is not valid".format(category.get(), i+1))
                frame.focus_force()
                return
            
            if name.get() == "":
                tkinter.messagebox.showwarning("Warning!", "The name on row {} must be a nonzero length string.".format(i+1))
                frame.focus_force()
                return
            
            
            doc = {"Name"     : name.get(),
                   "Date"     : datetime(year.get(), lookup.month_str_to_number[month.get().lower()], day.get()),
                   "Category" : category.get(),
                   "Amount"   : amount.get(),
                   "Courtney" : courtney.get(),
                   "Reurring" : recurring.get()}
            
            print(doc)
            #expenses.insert_one(doc)
        print()
        
    def populate_expenses(collection, frame, names, year, month, days, categories, amounts, courtneys, recurrings):
        last_month_i = lookup.month_str_to_number[month.get().lower()] - 1
        last_year_i  = year.get()
        if last_month_i == 0:
            last_month_i = 12
            last_year_i -= 1
            
        # Get the first and last days
        min_date = datetime(last_year_i, last_month_i, 1)
        # Use monthrange to get the last day of the month
        max_date = datetime(last_year_i, last_month_i, calendar.monthrange(last_year_i, last_month_i)[1]) 
        
        # Build the query    
        query = {"Recurring" : True, "Date" : {"$lte" : max_date, "$gte" : min_date}}

        # Find recurring expenses from the last month, and sort by date
        reccuring_docs = expenses.find(query).sort("Date", 1)
    

        for i, doc in enumerate(reccuring_docs):
            name, day, category, amount, courtney, recurring = expenseEntryFields(expense_values, expenses, year, month, row=i*2, submit=False,
                                                                                  default_name=doc["Name"],
                                                                                  default_day=doc["Date"].day,
                                                                                  default_category=doc["Category"],
                                                                                  default_amount=doc["Amount"],
                                                                                  default_courtney=doc["Courtney"],
                                                                                  default_recurring=doc["Recurring"])
            
            names.append(name)
            days.append(day)
            categories.append(category)
            amounts.append(amount)
            courtneys.append(courtney)
            recurrings.append(recurring)
        

    def refresh_expenses(collection, frame, names, year, month, days, categories, amounts, courtneys, recurrings):
        # Remove enteries first
        for label in frame.grid_slaves():
            label.grid_remove()
        
        # Reset each list
        names.clear()
        days.clear()
        categories.clear()
        amounts.clear()
        courtneys.clear()
        recurrings.clear()
        
        # re-populte the expenses frame
        populate_expenses(collection, frame, names, year, month, days, categories, amounts, courtneys, recurrings)
    
    #--------------------------------------------------------------------------
    # Load the database
    #--------------------------------------------------------------------------
    expenses = database.openCollection()
    
    #--------------------------------------------------------------------------
    # Tkinter Variables
    #--------------------------------------------------------------------------
    current_date = datetime.now()
    month        = tkinter.StringVar(value = current_date.strftime("%b"))
    year         = tkinter.IntVar(   value = current_date.year)
    #--------------------------------------------------------------------------
    
    expense_window = tkinter.Toplevel()
    expense_window.focus_set()
    expense_window.title("Recurring Expenses")
    expense_window.minsize(width=min_width, height=min_height)
    expense_window.resizable(width=True, height=True)
    
    top_frame = tkinter.Frame(expense_window)
    top_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    #--------------------------------------------------------------------------
    # Month/Year Selection
    #--------------------------------------------------------------------------
    month_frame = tkinter.LabelFrame(top_frame, text="Month")
    month_frame.grid(row=0, column=0, sticky="nesw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    month_w     = ttk.Combobox(month_frame, values=lookup.months_list, textvariable=month, width=5)
    year_w      = ttk.Entry(month_frame, textvariable=year, width=5)
    month_w.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    year_w.pack( side="left", anchor="w", padx=xpad, ipadx=ixpad)
        
    #--------------------------------------------------------------------------
    # The Expense Frame
    #--------------------------------------------------------------------------
    expense_values = tkinter.LabelFrame(expense_window, text="Recurring Expenses")    
    expense_values.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)

    names      = []
    days       = []
    categories = []
    amounts    = []
    courtneys  = []
    recurrings = []
    
    populate_expenses(expenses, expense_values, names, year, month, days, categories, amounts, courtneys, recurrings)
        
    #--------------------------------------------------------------------------
    # The Refresh Button
    #--------------------------------------------------------------------------
    refresh_bt = tkinter.Button(top_frame, text="Refresh Expenses", command=lambda:refresh_expenses(expenses, expense_values, names, year, month, days, categories, amounts, courtneys, recurrings))
    refresh_bt.grid(row=0, column=1, sticky="nesw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
        
    #--------------------------------------------------------------------------
    # The Controls
    #--------------------------------------------------------------------------    
    controls = tkinter.Frame(expense_window)
    controls.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # add aditional button
    add_bt = tkinter.Button(controls, text="Add Expense", command=lambda:add_recurring_expense(expense_values, names, days, categories, amounts, courtneys, recurrings))
    add_bt.pack(side="left", anchor="w", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # remove button
    remove_bt = tkinter.Button(controls, text="Remove Expense", command=lambda:remove_recurring_expense(expense_values, names, days, categories, amounts, courtneys, recurrings))
    remove_bt.pack(side="left", anchor="w", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    # submit button
    submit_bt = tkinter.Button(controls, text="Submit Expenses", command=lambda:submit_expenses(expenses, expense_values, names, year, month, days, categories, amounts, courtneys, recurrings))
    submit_bt.pack(side="left", anchor="w", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
#------------------------------------------------------------------------------

def monthQuery():
    """
    This defines the GUI for the user to complete a query for a specific month.

    Returns
    -------
    None.

    """
    def do_query(expenses):
        df, str_ym = database.getMonthSummary(month.get(), year.get(), expenses)
        database.save_dfs(df, os.path.join(path.get(), str_ym))
        
        tkinter.messagebox.showinfo("Complete", "The querys have been saved to file.")
        
        query_window.focus_force()

    def browse_folder():
        path.set(tkinter.filedialog.askdirectory())
        
        query_window.focus_force()
        
    #--------------------------------------------------------------------------
    # Load the database
    #--------------------------------------------------------------------------
    expenses = database.openCollection()
    
    #--------------------------------------------------------------------------
    # Tkinter Variables
    #--------------------------------------------------------------------------
    current_date = datetime.now()
    month        = tkinter.StringVar(value=current_date.strftime("%b"))
    year         = tkinter.IntVar(value=current_date.year)
    path         = tkinter.StringVar(value=os.path.abspath(os.path.join("..", "data")))
    #--------------------------------------------------------------------------
    
    query_window = tkinter.Toplevel()
    query_window.focus_set()
    query_window.title("Month Query")
    query_window.minsize(width=min_width, height=min_height)
    query_window.resizable(width=True, height=True)
    
    #--------------------------------------------------------------------------
    # Month/Year Selection
    #--------------------------------------------------------------------------
    month_frame = tkinter.LabelFrame(query_window, text="Month and Year to Query")
    month_w     = ttk.Combobox(month_frame, values=lookup.months_list, textvariable=month, width=5)
    year_w      = ttk.Entry(month_frame, textvariable=year, width=5)
    
    # Submit Button
    submit_bt = tkinter.Button(month_frame, text="Submit", command=lambda:do_query(expenses))

    
    month_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    month_w.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    year_w.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    submit_bt.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    
    
    save_frame = tkinter.LabelFrame(query_window, text="Save Location")
    save_frame.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    path_entry = tkinter.Entry(save_frame, textvariable=path, width=70)
    path_entry.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
    
    path_bt    = tkinter.Button(save_frame, text="Browse", command=browse_folder)
    path_bt.pack(side="left", anchor="w", padx=xpad, ipadx=ixpad)
#------------------------------------------------------------------------------

def openApp(message):
    """
    This is the top level window and the root for navigating the whole app.

    Parameters
    ----------
    message : String
        The about string is passed in from the main sofware call.

    Returns
    -------
    None.

    """
    def about():
        tkinter.messagebox.showinfo("About", message)
        
    top = tkinter.Tk()
    
    top.title("PyFinance")
    top.minsize(width=min_width, height=min_height)
    top.resizable(width=True, height=True)
    
    # Buttons
    master_buttons = tkinter.LabelFrame(top, text="Operations")
    master_buttons.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    enter_bt  = tkinter.Button(master_buttons, text="Enter Expense", command=enterExpense)
    enter_bt.pack(side="left", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    enter_rec_bt = tkinter.Button(master_buttons, text="Enter Recurring Expenses", command=enterRecurringExpenses)
    enter_rec_bt.pack(side="left", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    mquery_bt = tkinter.Button(master_buttons, text="Month Query", command=monthQuery)
    mquery_bt.pack(side="left", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
       
    mquery_bt = tkinter.Button(top, text="About", command=about)
    mquery_bt.pack(side="top", anchor="nw", padx=xpad, pady=ypad,ipadx=ixpad, ipady=iypad)
    
    top.mainloop()