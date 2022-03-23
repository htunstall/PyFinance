# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 00:02:37 2022

@author: Harry
"""
import pymongo

def openCollection(address="localhost", port=27017):
    myclient = pymongo.MongoClient(address, port)
    expenses = myclient.finances.expenses
    
    return expenses

