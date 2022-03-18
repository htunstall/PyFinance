# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 18:50:35 2022

@author: Harry
"""

import pymongo
import pandas as pd

from datetime import datetime

myclient = pymongo.MongoClient("localhost", 27017)
db       = myclient.finances
expenses = db.expenses
#------------------------------------------------------------------------------
print(expenses)


min_date = datetime(2021, 12, 1)
max_date = datetime(2021, 12, 31)

query = {"Date" : { "$lte" : max_date, "$gte" : min_date}}
query = {"Category" : "SUB"}
#query = {}

docs = expenses.find(query)

for d in docs:
    print(d)
    
print()
print(expenses.count_documents(query))

print()

df = pd.DataFrame(list(expenses.find(query)))

df.sort_values("Date", inplace=True)

print(df)

with open("test.html", "w") as f:
    df.to_html(f)
    
df.drop("_id", axis=1, inplace=True)
df.to_csv("test.csv", index=False)





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
    