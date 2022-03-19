# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 18:50:35 2022

@author: Harry
"""
import os
import pymongo
import calendar
import pandas as pd

from datetime import datetime
#------------------------------------------------------------------------------

def getMonthSummary(month, year, col, path="."):
    """
    This method creates a summary from the collection, saves them out and returns a Pandas DataFrame

    Parameters
    ----------
    month : Int/Str
        The month we are generating a summary for.
    year : Int
        The year we are generating a summary for.
    col : PyMongo Collection
        The collection we are querying.
    path : Str
        The path to where the output files are saved.

    Returns
    -------
    Pandas DataFrame with all the enteries for the month.

    """
        
    month_str_to_number = {"jan" : 1, "feb" : 2, "mar" : 3, "apr" : 4, "may" : 5, "jun" : 6, "jul" : 7, "aug" : 8, "sep" : 9, "oct" : 10, "nov" : 11, "dec" : 12}
    
    # Sanitise inputs
    if type(month) == str:
        month = month.lower()[:3]
        if month in month_str_to_number.keys():
            month = month_str_to_number[month]
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
    
    # Calculate Totals
    totals = {"Name" : "Totals", "Category": "TOTAL", "Date_fmt": "", "Amount" : df["Amount"].sum(), "Courtney" : df["Courtney"].sum()}
    
    # Place them at the end of the dataframe
    df = df.append(totals, ignore_index=True)
    
    # Create formatted cost rows
    df["Amount_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Amount"]).replace("£-", "-£"), axis=1)
    df["Courtney_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Courtney"]).replace("£-", "-£"), axis=1)
    
    return df
#------------------------------------------------------------------------------

def save_dfs(df, path="."):
    """
    Save att the relevent dataframes.

    Parameters
    ----------
    df : Pandas DataFrame
        The dataframe, usually a month summary.
        
    path : Str
        The path to where the output files are saved.

    Returns
    -------
    None.

    """
    def write_html(_df, name="default.html", cols=None):
        with open(os.path.join(path, name), "w", encoding="utf-8") as f:
            _df.to_html(f, columns=cols, col_space=150, justify="center", index=False)
    #--------------------------------------------------------------------------
    
    # Pretty formatting
    replace_dict = {"Date_fmt" : "Date", "Amount_fmt" : "Amount", "Courtney_fmt" : "Courtney", "Courtney" : "Courtney_num", "Amount" : "Amount_num", "Date" : "Date_dt"}
    #df_fmt       = df.drop(["Date", "Amount", "Courtney"], axis=1)
    df_fmt = df.rename(replace_dict, axis=1)
    
    
    # Save all to csv (all columns)
    df_fmt.to_csv("test.csv", index=False)
    
    # Save all to html
    write_html(df_fmt, "test.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    
    # Save just courtney to html
    c_df = df_fmt[df["Courtney"] != 0]
    write_html(c_df, "courtney.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    
    # Save just harry to html
    h_df = df_fmt[df["Courtney"] == 0]
    write_html(h_df, "harry.html", ["Name", "Date", "Category", "Amount"])
    
    
    # For each category
    for cat in df_fmt["Category"].unique():
        if cat != "TOTAL":
            w_df = df_fmt[df_fmt["Category"] == cat]
            
            # Calculate Totals
            totals = {"Name" : "Totals", "Category": "TOTAL", "Date": "",
                      "Amount" : "£{:0,.2f}".format(w_df["Amount_num"].sum()).replace("£-", "-£"),
                      "Courtney" : "£{:0,.2f}".format(w_df["Courtney_num"].sum()).replace("£-", "-£")}
    
            # Place them at the end of the dataframe
            w_df = w_df.append(totals, ignore_index=True)
            
        
            write_html(w_df, "{}.html".format(cat.lower()), ["Name", "Date", "Amount", "Courtney"])

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

myclient = pymongo.MongoClient("localhost", 27017)
db       = myclient.finances
expenses = db.expenses
#------------------------------------------------------------------------------


df = getMonthSummary("Jan", 2022, expenses)

save_dfs(df)

print(df)


    








    
