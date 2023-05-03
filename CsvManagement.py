#!/usr/bin/env python3


# ! - Libraries - ! #
import os
import csv
import datetime
import pandas as pd
from os.path import exists
from decimal import Decimal
from statistics import mode
from pprint import pprint as pp


class CsvManagement:

    # ! - Constants - ! #
    TIME_FORMAT_STR = '%H:%M' # Format used for time data.
    TWO_DP = Decimal(10) ** -2 # Set the number of decimal places.
    CSV_EXPORT = '_lib/shiftData.csv' # Set the export csv location.
    PAY_EXPORT = '_lib/paycheques.txt' # Set the paycheques file location.
    FIELDS = {
        "F_MONTH" : 0,
        "F_DAY" : 1,
        "F_START" : 2,
        "F_END" : 3,
        "F_DURATION" : 4,
        "F_PAID_HOURS" : 5
    } # Dictionary for the field names.
    MONTHS = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    } # Dictionary for replacing Month name with Month number.
    try:
        os.remove(PAY_EXPORT) # Remove the paycheques file.
    except:
        pass


    # ! - Functions - ! #
    def __init__(self): # Always run.
        self.ifMain = ifMain = False # Initialise and set to False.
        if __name__ == "__main__": self.ifMain = ifMain = True # If this is Main, set to True.


    # >>> Create a 2D array.
    def create2DArray(self, column, row):
        array = [[0 for _ in range(column)] for _ in range(row)] # The code to create one, using the two parameters that were passed.
        return array # Return this 2D array.
    

    # >>> Clear arrays.
    def clearArrays(self):
        self.yearArray = []
        self.monthArray = []
        self.dayArray = []
        self.startArray = []
        self.endArray = []
        self.durationArray = []
        self.paidHoursArray = []


    # >>> Select csv file.
    def selectFile(self):

        # >>> Get csv file path from user input and validate.
        while True: # Loop until valid user input.
            self.CSV_FILE = input("\nEnter the file path of the CSV file:\nFile path -> ").strip().strip("\"'") # Ask for the csv file path.
            if self.CSV_FILE == ('q' or 'Q'): # If user wants to quit,
                return True # return True.
            if exists(self.CSV_FILE): # If file exists, user input is valid,
                return False # return False.
            print("\n! >>> ERROR - File does not exist, try again.") # Say the user input is invalid.


    # >>> Get the data from the csv file.
    def getCSVData(self):

        # >>> Get the number of records.
        self.recordCount = 0
        with open(self.CSV_FILE, 'r') as csvFile: # Open the CSV file under csvFile.
            lines = csv.reader(csvFile, delimiter=',') # Grab the data.
            next(lines) # Remove the headers.
            for row in lines: # For every row ...
                for column in row: # ... for every column ...
                    if column != '': # ... if the column is not empty:
                        if ":" in column:
                            self.recordCount += 1 # Increment recordCount.
        csvFile.close() # Close the csvFile.


        # >>> Get data from CSV file.
        with open(self.CSV_FILE, 'r') as csvFile: # Open the CSV file under csvFile.
            lines = csv.reader(csvFile, delimiter=',') # Grab the data.
            next(lines) # Remove the headers.
            for row in lines: # For every row ...
                for column in row: # ... for every column ...
                    if column != '': # ... if the column is not empty:
                        if ":" in column:
                            splitColumn = column.split('\n') # Split by '\n'.
                            splitDates = splitColumn[0].split(' ') # Split by ' '.
                            splitTimes = splitColumn[2].split(' - ') # Split by ' - '.
                            self.monthArray.append(splitDates[1]) # Append to monthArray.
                            self.dayArray.append(splitDates[0]) # Append to dayArray.
                            self.startArray.append(splitTimes[0]) # Append to startArray.
                            self.endArray.append(splitTimes[1]) # Append to endArray.
        return self.recordCount # Return recordCount.


    # >>> Process the CSV data.
    def processCSVData(self):

        # >>> Replace the Month Names with the Month Numbers.
        self.monthArray = [ str(self.MONTHS[monthName]).zfill(2) for monthName in self.monthArray ] # Switch Month names to Month numbers.

        # >>> Turn dayArray from string to integer values.
        self.dayArray = [ str(day).zfill(2) for day in self.dayArray] # Make all values strings with leading Zeros.

        # >>> Make the start times 24Hr.
        self.startArray = [ start.replace("AM", '').replace("PM", '').strip() for start in self.startArray ] # Strip AM.

        # >>> Make the end times 24HR.
        self.endArray = [ end.replace("AM", '').replace("PM", '').strip() for end in self.endArray ] # Strip PM.
        self.endArray = [ str(int(end.split(':')[0]) + 12) + ':' + end.split(':')[1] for end in self.endArray ] # Format to 24Hr.

        # >>> Create and fill duration array.
        for i in range(self.recordCount):
            startTime = pd.to_datetime(self.startArray[i], format=self.TIME_FORMAT_STR) # Format and set the start time.
            endTime = pd.to_datetime(self.endArray[i], format=self.TIME_FORMAT_STR) # Format and set the end time.
            diffTime = ((endTime - startTime).total_seconds() / 3600) # Calculate the difference, divide into hours.
            self.durationArray.append(diffTime) # Append result to array.
            self.paidHoursArray.append(diffTime - 0.50) # Subtract half an hour break, append result to array.

        # >>> Isolate the unnecessary months.
        mostCommonMonth = mode(self.monthArray)
        removedIndexes = []
        for i in range(len(self.monthArray)): # For every month ...
            if self.monthArray[i] != mostCommonMonth: # ... if the month is not the most common month ...
                removedIndexes.append(i) # ... add the index to the removedIndexes array.

        # >>> Remove the unnecessary months.
        removedIndexes.reverse() # Reverse the list.
        for i in removedIndexes: # For every element in removedIndexes ...
            del self.monthArray[i], self.dayArray[i], self.startArray[i], self.endArray[i], self.durationArray[i], self.paidHoursArray[i] # ... delete the index from all tables.
        self.recordCount = self.recordCount - len(removedIndexes) # Update the record count.



    # >>> Combine data.
    def combineData(self):

        # >>> Create the 2D table for all the data.
        self.dataArray = self.create2DArray(len(self.FIELDS), self.recordCount)

        # >>> Create a row of combined data and add it to the dataArray.
        for i in range(self.recordCount): # For every record ...
            row = [self.monthArray[i], self.dayArray[i], self.startArray[i], self.endArray[i], self.durationArray[i], self.paidHoursArray[i]] # ... create a row of combined data ...
            self.dataArray[i] = row # ... and add it to the dataArray.


    # >>> Export all the data.
    def exportAllData(self, allTablesData):

        with open(self.CSV_EXPORT, 'w') as csvFile: # Prepare to write the csv file.
            writer = csv.writer(csvFile)

            for table in allTablesData: # For every table,
                writer.writerows(table) # write the table to the file.

        csvFile.close() # Close the csv file.


    # >>> Export paycheques data.
    def exportPaychequeData(self, nextPaymentDate, payChequeFormatted):
        
        payFile = open(self.PAY_EXPORT, 'a') # Prepare to append to the paycheque file.
            
        payFile.write(nextPaymentDate) # Write the paycheque date,
        payFile.write(' | ') # add the separator,
        payFile.write(payChequeFormatted) # add the paycheque price,
        payFile.write('\n') # add the new line character.

        payFile.close() # Close the paycheques file.
        


# ! - \/ \/ \/ \/ \/ - ! #
# ! - - -  Main  - - - ! #
if __name__ == "__main__":

    initCSV = CsvManagement() # Initiate the Class.

    initCSV.selectFile() # Select the file.
    initCSV.getCSVData() # Get the CSV data.
    initCSV.processCSVData() # Process this data.
    initCSV.combineData() # Combine all the data.
