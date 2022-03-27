"""
All the database logic and minipulation happens in this module.
"""

import os
import pymongo
import calendar
import pandas   as pd
from   datetime import datetime

#------------------------------------------------------------------------------
def openCollection(address="localhost", port=27017):
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
    
    
    # Create formatted cost rows
    df["Amount_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Amount"]).replace("£-", "-£"), axis=1)
    df["Courtney_fmt"] = df.apply(lambda row: "£{:0,.2f}".format(row["Courtney"]).replace("£-", "-£"), axis=1)
    
    return df, min_date.strftime("%Y-%m_%B")

#------------------------------------------------------------------------------
def save_dfs(df, root="."):
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
    df_fmt.to_csv(os.path.join(root, "month-overview.csv"), index=False)
    
    # Save all to html
    # Calculate Totals
    totals = {"Name" : "Totals", "Category": "TOTAL", "Date_fmt": "",
              "Amount"   : "£{:0,.2f}".format(df_fmt["Amount_num"].sum()).replace("£-", "-£"),
              "Courtney" : "£{:0,.2f}".format(df_fmt["Courtney_num"].sum()).replace("£-", "-£")}
    
    # Place them at the end of the dataframe
    df_all = df_fmt.append(totals, ignore_index=True)
    
    df_all_value = df_all.sort_values("Amount_num")
    
    write_html(df_all,       "month-overview.html", ["Name", "Date", "Category", "Amount", "Courtney"])
    write_html(df_all_value, "month-overview.html", ["Name", "Date", "Category", "Amount", "Courtney"], value_root)
    
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