#!/usr/bin/env python3


# ! - Libraries - ! #
import csv
import sys
import hashlib
import pandas as pd
import sqlite3 as lite
from pprint import pprint as pp


class DatabaseManagement:

    # ! - Functions - ! #
    def __init__(self): # Always run.
        self.ifMain = False # Initialise and set to False.
        if __name__ == "__main__": self.ifMain = True # If this is Main, set to True.

        self.DB_FILE = "_lib/ShiftData.db"

        try:
            self.connection = lite.connect(self.DB_FILE) # Connect to the test database file.
        except Exception as e:
            print(f"Please create a folder in the directory called \"_lib\"")
            print(e)
            sys.exit()

        self.cursor = self.connection.cursor() # Add the cursor (idek, it just needs to exist).


    # >>> Get the hash of the database file.
    def hashFile(self):
        with open(self.DB_FILE, 'rb'): # Open the file,
            return hashlib.md5(open(self.DB_FILE, 'rb').read()).hexdigest() # and return the hash of the file.


    # >>> Delete data from database.
    def deleteData(self, tableName):
        self.cursor.execute("DROP TABLE IF EXISTS \"" + tableName + "\"") # Delete the table.


    # >>> Get table names from database.
    def getTableNames(self):

        tableNames = [] # Initialise tableNames array.
        data = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # Get database data.
        for name in data.fetchall(): # Filter the data.
            tableNames.append(name[0]) # Append the names to the tableNames array.
        tableNames.sort(reverse=True) # Sort, with most recent month first.
        tableNames.remove("PayDataTable") # Remove the PayDataTable from the list.
        return tableNames # Return the table names


    # >>> Get data from database.
    def getTableData(self, tableName):

        self.cursor.execute("SELECT * FROM \"" + tableName + "\" ORDER BY columnDay ASC") # Select the month data.
        monthData = self.cursor.fetchall() # Fetch the selected data.

        return monthData # Return the month data.


    # >>> Get pay cheque data.
    def getPayChequeData(self, previousTableName, tableName, DIVIDER_DAY):

        self.cursor.execute("SELECT columnPaidHours FROM \"" + previousTableName + "\" WHERE columnDay>" + DIVIDER_DAY) # Select the previous month data. (Previously thought it was 14th)
        previousMonthData = self.cursor.fetchall() # Fetch the selected data.

        self.cursor.execute("SELECT columnPaidHours FROM \"" + tableName + "\" WHERE columnDay<=" + DIVIDER_DAY) # Select the month data. (Previously thought it was 14th)
        currentMonthData = self.cursor.fetchall() # Fetch the selected data.

        shiftCount = len(previousMonthData) + len(currentMonthData) # Calculate the number of shifts.

        return previousMonthData, currentMonthData, shiftCount # Return the month data.


    # >>> Calculate the pay cheque.
    def calculatePayCheque(self, previousMonthData, currentMonthData):

        previousMonthTotalHours = 0 # Reset the previousMonthTotalHours.
        for x in previousMonthData: # For every element in previousMonthData,
            previousMonthTotalHours += x[0] # add this value to the previousMonthTotalHours.

        currentMonthTotalHours = 0 # Reset the currentMonthTotalHours.
        for y in currentMonthData: # For every element in currentMonthData,
            currentMonthTotalHours += y[0] # add this value to the currentMonthTotalHours.

        return previousMonthTotalHours, currentMonthTotalHours # Return the total hours.


    # >>> Write data to database.
    def saveData(self, dataArray, CURRENT_YEAR, CURRENT_MONTH):

        month = dataArray[0][0] # Get the month.
        year = CURRENT_YEAR # Set the year to current year.

        if int(month) < int(CURRENT_MONTH): # If the month is before the current month,
            print(f"Is {month} replacement data? Or for next year?")
            print("1)", year)
            print("2)", int(year) + 1)
            while True: # get the year the user wants.
                try:
                    choice = int(input("#? ").strip()) # Get the year input as an integer.
                    if choice == 2: year = str(int(year) + 1) # If the choice is 2, choose the next year.
                    break # Break from the loop.
                except:
                    continue # Else continue.        

        tableName = year + "_" + month # Format the table name from the year and month.

        self.deleteData(tableName) # Delete the existing data.

        columns = "(columnYear INT, columnMonth INT, columnDay INT, columnStartTime CHAR(5), columnEndTime CHAR(5), columnDuration DOUBLE(4,2), columnPaidHours DOUBLE(4,2))" # Setup the columns of the table.
        self.cursor.execute("CREATE TABLE IF NOT EXISTS \"" + tableName + "\" " + columns) # Create the table.

        for i in range(len(dataArray)): # For every row, insert the data.
            self.cursor.execute("INSERT INTO \"" + tableName + "\" " + " VALUES (?,?,?,?,?,?,?)",(year,dataArray[i][0],dataArray[i][1],dataArray[i][2],dataArray[i][3],dataArray[i][4],dataArray[i][5]))

        self.connection.commit() # Commit the connecton.

        return tableName # Return the tableName.


    # >>> Create the pay data table.
    def createPayDataTable(self):
        columns = "(tableName CHAR(7), payPerHour DOUBLE(4,2))" # Setup the columns of the table.
        self.cursor.execute("CREATE TABLE IF NOT EXISTS \"PayDataTable\" " + columns) # Create the table.
        self.connection.commit() # Commit the connecton.


    # >>> Save a new table to the pay data table.
    def saveNewPayData(self, tableName):
        payAmount = self.getPreviousPayData() # Get the previous pay amount.
        self.cursor.execute("SELECT \"tableName\" FROM \"PayDataTable\" WHERE \"tableName\"=?;",[tableName]) # See if there is any data for this tableName.
        data = self.cursor.fetchall() # Fetch the selected data.
        if len(data) > 0: # If there are tableName values already, delete them.
            self.cursor.execute("DELETE FROM \"PayDataTable\" WHERE \"tableName\"=?;",[tableName]) # Insert pay data into table.
            self.connection.commit() # Commit the connecton.
        self.cursor.execute("INSERT INTO \"PayDataTable\" VALUES (?,?)",(tableName,payAmount)) # Insert pay data into table.
        self.connection.commit() # Commit the connecton.


    # >>> Pay data table.
    def editPayDataTable(self, tableName, newPay):
        self.cursor.execute("UPDATE \"PayDataTable\" SET payPerHour=? WHERE tableName=?",(newPay,tableName)) # Update pay per hour.
        self.connection.commit() # Commit the connecton.
        print("\nPay for %s has changed to £%.2f" % (tableName, newPay), end='') # Say that we've done it.


    # >>> Get the previous pay per hour from last month.
    def getPreviousPayData(self):
        self.cursor.execute("SELECT \"payPerHour\" FROM \"PayDataTable\" ORDER BY \"tableName\" DESC") # Update pay per hour.
        data = self.cursor.fetchall() # Fetch the selected data.
        try: # Try to return the value.
            return float(str(data[0]).strip("(),")) # Strip excess characters and put back to float.
        except: # If no value, return ZERO.
            return 0.0


    # >>> Get the previous pay per hour from last month.
    def getHourlyPay(self, tableName):
        self.cursor.execute("SELECT \"payPerHour\" FROM \"PayDataTable\" WHERE \"tableName\" = \"" + tableName + "\"") # Update pay per hour.
        data = self.cursor.fetchone() # Fetch the selected data.
        try: # Try to return the value.
            return float(str(data).strip("(),")) # Strip excess characters and put back to float.
        except: # If no value, return ZERO.
            return 0.0


    # >>> Get all of the data from the database.
    def getAllData(self, tableNames):

        allTablesData = [] # Initiate the array.
        for tableName in tableNames: # For every table,
            self.cursor.execute("SELECT * FROM \"" + tableName + "\"") # select the data,
            allTablesData.append(self.cursor.fetchall()) # then fetch and save it to the allTablesData array.

        return allTablesData # Return this data.
    
    
    # >>> Get the total shift count.
    def getTotalShiftCount(self, allTablesData):
        
        totalShiftCount = 0 # Initialise the total shift counter.
        for table in allTablesData: # For every table in all tables data.
            for shift in table: # For every shift in the table.
                totalShiftCount += 1 # Increment the total shift count.
                
        return totalShiftCount # Return the total shift count.

    
    # >>> Get the total amount earned.
    def getTotalAmountEarned(self, tableNames):
        
        totalAmountEarned = 0 # Initialise the total amount earned.
        for tableName in tableNames: # For every table name in table names.
            hourlyPay = self.getHourlyPay(tableName) # Get the hourly pay for the table.
            for shift in self.getTableData(tableName): # For every shift in the current table.
                totalAmountEarned += hourlyPay * shift[5] # Add the hourly pay multiplied by the shift hours.
                
        return totalAmountEarned # Return the total shift count.
    
    
    # >>> Get the total hours worked.
    def getTotalHoursWorked(self, allTablesData):
        
        totalHoursWorked = 0 # Initialise the total hours worked.
        for table in allTablesData: # For every table in all tables data.
            for shift in table: # For every shift in the table.
                totalHoursWorked += shift[5] # Increment the total shift count.
        
        return totalHoursWorked # Return the total shift count.
    
    
    # >>> Get all of the statistic data.
    def getAllStatisticData(self, tableNames):
        
        allTablesData = self.getAllData(tableNames) # Get all the data from the database.
        
        totalShiftCount = self.getTotalShiftCount(allTablesData) # Get the total shift count.
        totalAmountEarned = self.getTotalAmountEarned(tableNames) # Get the total amount earned.
        totalHoursWorked = self.getTotalHoursWorked(allTablesData) # Get the total hours worked.
        
        return (totalShiftCount, totalAmountEarned, totalHoursWorked) # Return the statistic data.


    # >>> Calculate the deductions and return new value.
    def calculateDeductions(self, grossPay):
        
        NI_MINIMUM = 1048.01 # Current national insurance boundary
        NI_PERCENT = 1 - 0.12 # Current national insurance percentage
        
        if grossPay >= NI_MINIMUM: # If the pay needs to be deducted.
            return grossPay * NI_PERCENT # return the deducted amount.
        
        return grossPay # Else return the value unchanged.



# ! - \/ \/ \/ \/ \/ - ! #
# ! - - -  Main  - - - ! #
if __name__ == "__main__":
    
    print("File is dependent.")

    # initDBM = DatabaseManagement() # Initialise the class.

    # initDBM.getTableNames()

    # initDBM.connection.commit() # Close the database.
