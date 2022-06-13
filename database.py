"""
All the database logic and minipulation happens in this module.
"""

import os
import pymongo
import calendar
import pandas   as pd
from   datetime import datetime

import lookup

#------------------------------------------------------------------------------
def openCollection(address, port):
    """
    Open the collection expenses located in the database finances from the
    MongoDB and return it.

    Parameters
    ----------
    address : String, optional
        The address of the MongoDB server. The default is "localhost".
    port : Integer, optional
        The port the MongoDB server is running on. The default is 27017.

    Returns
    -------
    expenses : pymongo Collection
        This is the expenses Collection where the data is stored.

    """
    myclient = pymongo.MongoClient(address, port)
    expenses = myclient.finances.expenses
    
    return expenses

#------------------------------------------------------------------------------
def getMonthSummary(month, year, col, path="."):
    """
    This method creates a summary from the collection, saves them out and returns a Pandas DataFrame

    Parameters
    ----------
    month : Integer/String
        The month we are generating a summary for.
    year : Integer
        The year we are generating a summary for.
    col : PyMongo Collection
        The collection we are querying.
    path : String, optional
        The path to where the output files are saved.

    Returns
    -------
    Pandas DataFrame with all the enteries for the month.

    """
    
    # Sanitise inputs
    if type(month) == str:
        month = month.lower()[:3]
        if month in lookup.month_str_to_number.keys():
            month = lookup.month_str_to_number[month]
        else:
            raise KeyError("The month string input is not understood, and cannot be converted")
    elif type(month) == int:
        if month < 1 or month > 12:
            raise Exception("The month integer is not a valid month")
    else:
        raise TypeError("The month input is not the correct type")
        
    if type(year) != int:
        raise TypeError("The year must be an integer")
    #--------------------------------------------------------------------------
    
    # Get the first and last days
    min_date = datetime(year, month, 1)
    # Use monthrange to get the last day of the month
    max_date = datetime(year, month, calendar.monthrange(year, month)[1]) 
    
    # Build the query
    query = {"Date" : { "$lte" : max_date, "$gte" : min_date}}
    
    # Find the documents, and save them to a dataframe
    df = pd.DataFrame(list(col.find(query)))
        
    # Sort the values into chronological order
    df.sort_values("Date", inplace=True)
    
    # Create formated date
    df["Date_fmt"] = df["Date"].dt.strftime("%d-%b-%Y")
    
    
    # Create formatted cost rows
    df["Amount_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Amount"]).replace("£-", "-£"), axis=1)
    df["Courtney_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Courtney"]).replace("£-", "-£"), axis=1)
    
    return df, min_date.strftime("%Y-%m_%B")

#------------------------------------------------------------------------------
def saveDF(df, root="."):
    """
    Save att the relevent dataframes.

    Parameters
    ----------
    df : Pandas DataFrame
        The dataframe, usually a month summary.
        
    root : String, optional
        The path to the root directory where the output files are saved.

    Returns
    -------
    None.

    """
    def write_html(_df, name="default.html", cols=None, _root=root):
        with open(os.path.join(_root, name), "w", encoding="utf-8") as f:
            _df.to_html(f, columns=cols, col_space=150, justify="center", index=False)
    #--------------------------------------------------------------------------
    
    value_root = os.path.join(root, "value_sorted")
    
    if not os.path.isdir(root):
        os.makedirs(root)
        
    if not os.path.isdir(value_root):
        os.makedirs(value_root)
    #--------------------------------------------------------------------------    
       
    # Pretty formatting
    replace_dict = {"Date_fmt" : "Date", "Amount_fmt" : "Amount", "Courtney_fmt" : "Courtney", "Courtney" : "Courtney_num", "Amount" : "Amount_num", "Date" : "Date_dt"}
    df_fmt = df.rename(replace_dict, axis=1)
    
    #--------------------------------------------------------------------------
    # All Enteries
    #--------------------------------------------------------------------------
    # Save all to csv (all columns)
    df_fmt.to_csv(os.path.join(root, "overview.csv"), index=False)
    
    # Save all to html
    # Calculate Totals
    # Total Recurring
    total_rec_amount   = df_fmt.loc[df_fmt["Recurring"] == True]["Amount_num"].sum()
    total_rec_courtney = df_fmt.loc[df_fmt["Recurring"] == True]["Courtney_num"].sum()
    
    total_rec = {"Name" : "Recurring Expenses Total", "Category": "TOTAL", "Date_fmt": "", "Date": "", "Recurring" : True,
                 "Amount"   : "£{:0,.2f}".format(total_rec_amount).replace("£-", "-£"),
                 "Courtney" : "£{:0,.2f}".format(total_rec_courtney).replace("£-", "-£")}
    
    
    total_exp_amount   = df_fmt.loc[df_fmt["Recurring"] == False]["Amount_num"].sum()
    total_exp_courtney = df_fmt.loc[df_fmt["Recurring"] == False]["Courtney_num"].sum()
    # Total Expenses
    total_exp = {"Name" : "Itemised Expenses Total", "Category": "TOTAL", "Date_fmt": "", "Date": "", "Recurring" : False,
                 "Amount"   : "£{:0,.2f}".format(total_exp_amount).replace("£-", "-£"),
                 "Courtney" : "£{:0,.2f}".format(total_exp_courtney).replace("£-", "-£")}
    
    total_gnd = {"Name" : "Grand Total", "Category": "TOTAL", "Date_fmt": -1, "Date": "", "Recurring" : True,
                 "Amount":   "£{:0,.2f}".format(total_rec_amount   + total_exp_amount).replace("£-", "-£"),
                 "Courtney": "£{:0,.2f}".format(total_rec_courtney + total_exp_courtney).replace("£-", "-£")}
    
    # Place them at the end of the dataframe
    df_all = df_fmt.append([total_rec, total_exp, total_gnd], ignore_index=True)
    
    df_all = df_all.sort_values(["Recurring", "Date_fmt"], ascending=[False, True])
        
    df_all_value = df_all.sort_values(["Amount_num", "Date_fmt"], ascending=[True, False])
    
    write_html(df_all,       "overview.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(df_all_value, "overview.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
    #--------------------------------------------------------------------------
    # All Positive/Negative Enteries
    #--------------------------------------------------------------------------
    # Save all to csv (all columns)
    df_positive = df_fmt.loc[(df_fmt["Amount_num"] > 0) & (df_fmt["Recurring"] == False)].sort_values("Amount_num")
    df_negative = df_fmt.loc[(df_fmt["Amount_num"] < 0) & (df_fmt["Recurring"] == False)].sort_values("Amount_num")
    
    # Save all to html
    # Calculate Totals
    positive_totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
                       "Amount"   : "£{:0,.2f}".format(df_positive["Amount_num"].sum()).replace("£-", "-£"),
                       "Courtney" : "£{:0,.2f}".format(df_positive["Courtney_num"].sum()).replace("£-", "-£")}
    
    negative_totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
                       "Amount"   : "£{:0,.2f}".format(df_negative["Amount_num"].sum()).replace("£-", "-£"),
                       "Courtney" : "£{:0,.2f}".format(df_negative["Courtney_num"].sum()).replace("£-", "-£")}
    
    # Place them at the end of the dataframe
    df_positive = df_positive.append(positive_totals, ignore_index=True).sort_values("Date", ascending=True)
    df_positive_value = df_positive.sort_values("Amount_num")
    
    df_negative = df_negative.append(negative_totals, ignore_index=True).sort_values("Date", ascending=True)
    df_negative_value = df_negative.sort_values("Amount_num")
    
    write_html(df_positive,       "positive-expenses.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(df_positive_value, "positive-expenses.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
    write_html(df_negative,       "negative-expenses.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(df_negative_value, "negative-expenses.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
    #--------------------------------------------------------------------------
    # Courtney Only Enteries
    #--------------------------------------------------------------------------
    # Save just courtney to html
    c_df = df_fmt[df["Courtney"] != 0]
    
    # Calculate Totals
    totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
              "Amount"   : "£{:0,.2f}".format(c_df["Amount_num"].sum()).replace("£-", "-£"),
              "Courtney" : "£{:0,.2f}".format(c_df["Courtney_num"].sum()).replace("£-", "-£")}

    # Place them at the end of the dataframe
    c_df = c_df.append(totals, ignore_index=True)
    
    c_df_value = c_df.sort_values("Courtney_num")
    
    write_html(c_df,       "courtney.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(c_df_value, "courtney.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
    #--------------------------------------------------------------------------
    # Harry Only Enteries
    #--------------------------------------------------------------------------
    # Save just harry to html
    h_df = df_fmt[df["Courtney"] == 0]
    
    # Calculate Totals
    totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
              "Amount"   : "£{:0,.2f}".format(h_df["Amount_num"].sum()).replace("£-", "-£"),
              "Courtney" : "£{:0,.2f}".format(h_df["Courtney_num"].sum()).replace("£-", "-£")}

    # Place them at the end of the dataframe
    h_df = h_df.append(totals, ignore_index=True)
    
    h_df_value = h_df.sort_values("Amount_num")
    
    write_html(h_df,       "harry.html", ["Name", "Date", "Category", "Amount"])
    write_html(h_df_value, "harry.html", ["Name", "Date", "Category", "Amount"], value_root)
    
    #--------------------------------------------------------------------------
    # Recurring Only Enteries
    #--------------------------------------------------------------------------
    # Save just harry to html
    rec_df = df_fmt[df["Recurring"] == True]
    
    # Calculate Totals
    totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
              "Amount"   : "£{:0,.2f}".format(rec_df["Amount_num"].sum()).replace("£-", "-£"),
              "Courtney" : "£{:0,.2f}".format(rec_df["Courtney_num"].sum()).replace("£-", "-£")}

    # Place them at the end of the dataframe
    rec_df = rec_df.append(totals, ignore_index=True)
    
    rec_df_value = rec_df.sort_values("Amount_num")
    
    write_html(rec_df,       "recurring.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(rec_df_value, "recurring.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
    
    #--------------------------------------------------------------------------
    # Each Category
    #--------------------------------------------------------------------------
    # For each category
    for cat in df_fmt["Category"].unique():
        if cat != "TOTAL":
            w_df = df_fmt[df_fmt["Category"] == cat]
            
            # Calculate Totals
            totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
                      "Amount"   : "£{:0,.2f}".format(w_df["Amount_num"].sum()).replace("£-", "-£"),
                      "Courtney" : "£{:0,.2f}".format(w_df["Courtney_num"].sum()).replace("£-", "-£")}
    
            # Place them at the end of the dataframe
            w_df       = w_df.append(totals, ignore_index=True)
            w_df_value = w_df.sort_values("Amount_num")
        
            write_html(w_df,       "{}.html".format(cat.lower()), ["Name", "Date", "Amount", "Courtney"])
            write_html(w_df_value, "{}.html".format(cat.lower()), ["Name", "Date", "Amount", "Courtney"], value_root)