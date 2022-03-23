# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 18:50:35 2022

@author: Harry
"""
import os
import database

#------------------------------------------------------------------------------

expenses   = database.openCollection()

df, str_ym = database.getMonthSummary("Jan", 2022, expenses)

database.save_dfs(df, os.path.join("..", "data", str_ym))

print(df)


    








    
