#!/usr/bin/env python3


# ! - Libraries - ! #
import os
import datetime as dt
from pprint import pprint as pp
from MenuOptions import MenuOptions
from CsvManagement import CsvManagement
from DatabaseManagement import DatabaseManagement


class Main:

    # ! - Functions - ! #
    def __init__(self):

        # ! -  Classes  - ! #
        self.mO = MenuOptions()
        self.cM = CsvManagement()
        self.dM = DatabaseManagement()

        self.dM.createPayDataTable() # Create the pay data table if it does not already exist.

        try: # Try to hash the database.
            self.ORIGINAL_MD5 = self.dM.hashFile() # Save the original MD5 for the database.
        except: # Else the database doesn't exist, so say so and move on.
            self.ORIGINAL_MD5 = "0"
            print("No db to hash yet.")

        self.CURRENT_YEAR  = str(dt.date.today().year)  # Set the current year.
        self.CURRENT_MONTH = str(dt.date.today().month) # Set the current month.
        self.CURRENT_DAY   = str(dt.date.today().day)   # Set the current day.

        self.continueProgram = True

        self.DIVIDER_DAY = "16"
        self.PAY_DAY = "28"
        
        self.DELETE_CSV = True


    # >>> Show the dashboard.
    def showDashboard(self, doPrint):
        self.mO.workOutPaymentDay(self.CURRENT_YEAR, self.CURRENT_MONTH, self.PAY_DAY) # Update mO class pay dates.

        if int(self.CURRENT_DAY) > int(self.mO.payDay): # If the current date is after this months payday, get next month.
            self.mO.workOutPaymentDay(self.CURRENT_YEAR, str(int(self.CURRENT_MONTH) + 1), self.PAY_DAY) # Add one month if it's past the payday.

        tableName = "%s_%02d" % (self.mO.payYear, int(self.mO.payMonth)) # Get the month table name.
        previousMonthTableName = "%s_%02d" % (self.mO.payYear, int(self.mO.payMonth) - 1) # Get the previous month table name.

        try:
            payChequeValue = self.calculatePayChequeChoice(previousMonthTableName, tableName, False) # Try get the pay cheque value.
        except:
            payChequeValue = 0.00 # If it fails, set to ZERO.

        self.mO.dashboard(payChequeValue, doPrint) # Launch the dashboard, and get the dashboard data.


    # >>> Calculate pay cheque.
    def calculatePayChequeChoice(self, previousMonthTableName, tableName, doPrint):
        previousMonthData, currentMonthData, shiftCount = self.dM.getPayChequeData(previousMonthTableName, tableName, self.DIVIDER_DAY) # Get the hours data.
        previousMonthTotalHours, currentMonthTotalHours = self.dM.calculatePayCheque(previousMonthData, currentMonthData) # Calculate the total hours.
        previousHourlyPay = self.dM.getHourlyPay(previousMonthTableName)
        currentHourlyPay = self.dM.getHourlyPay(tableName)
        totalHours = previousMonthTotalHours + currentMonthTotalHours
        totalPay = previousMonthTotalHours * previousHourlyPay + currentMonthTotalHours * currentHourlyPay
        payChequeValue = self.mO.printPayCheque(tableName, shiftCount, totalHours, totalPay, doPrint) # Print this data.
        return payChequeValue


    # >>> Choose month data.
    def viewMonthDataChoice(self):
        tableNames = self.dM.getTableNames() # Get the names of all the tables.
        tableName = self.mO.chooseTableName(tableNames, "What month would you like to view?\n") # Choose the table name from the list of table names.
        if tableName == "quit": return # If the user wants to quit, we quit.
        while True: # Repeat until broken.
            monthData = self.dM.getTableData(tableName) # Get the data from the table.
            self.mO.printMonthData(tableName, monthData) # Print this data.
            if ( tableNames.index(tableName) == 0 ): # If we are at index ZERO,
                print("\nFurthest recorded month.") # tell the user.
            elif ( tableNames.index(tableName) == (len(tableNames) - 1) ): # If we are at the last index,
                print("\nEarliest recorded month.") # tell the user.
            shiftMonthCheck = input("WASD? ").upper() # See whether the user wants to an adjacent month.
            if  ( ( shiftMonthCheck == 'W' ) or ( shiftMonthCheck == 'D' ) ): # If the user enters W or D,
                if ( tableNames.index(tableName) != 0 ): # and we are not at index ZERO,
                    tableName = tableNames[tableNames.index(tableName)-1] # view next month.
            elif ( shiftMonthCheck == 'A' ) or ( shiftMonthCheck == 'S' ) : # If the user enters A or S,
                if ( tableNames.index(tableName) != (len(tableNames) - 1) ): # and we are not at the last index,
                    tableName =  tableNames[tableNames.index(tableName)+1] # view previous month.
            else: return # Else return to the main program.


    # >>> Import a new csv file.    
    def importANewCSVFileChoice(self):
        # self.cM.clearArrays() # Clear all of the arrays.
        if self.cM.selectFile(): return # Select the csv file, and if the user has entered Q, quit.
        for self.cM.CSV_FILE in self.cM.CSV_FILES: # For every file in csv files:
            self.cM.clearArrays() # Clear all of the arrays.
            self.cM.getCSVData() # Get the data from the csv file.
            self.cM.processCSVData() # Save the data from the csv file
            self.cM.combineData(self.DELETE_CSV) # Combine the data into one 2D array.
            self.dM.saveData(self.cM.dataArray, self.CURRENT_YEAR, self.CURRENT_MONTH) # Save the data from the 2D array to the database.
            tableName = self.dM.getTableNames()[0] # Get the most recent table name.
            self.dM.saveNewPayData(tableName) # Forward the pay data to the next month.
        print("\nDone.", end='') # Tell the user that we are done importing the new csv file.


    # >>> Edit pay data.
    def editPayDataChoice(self):
        tableNames = self.dM.getTableNames() # Get the names of all the tables.
        tableName = self.mO.chooseTableName(tableNames, "What month would you like to edit pay data for?\n") # Choose the table name from the list of table names.
        if tableName == "quit": return # If the user wants to quit, we quit.
        newPay = self.mO.inputNewPayPerHour() # Get the new pay per hour.
        if newPay == "quit": return # If the user wants to quit, we quit.
        self.dM.editPayDataTable(tableName, newPay) # Set the new pay amount for the tableName.
        
    
    # >>> Show overall statistics.
    def showOverallStatistics(self):
        tableNames = self.dM.getTableNames() # Get the names of all the tables.
        (totalShiftCount, totalAmountEarned, totalHoursWorked) = self.dM.getAllStatisticData(tableNames) # Get the statistic data.
        self.mO.printStatisticData(totalShiftCount, totalAmountEarned, totalHoursWorked) # Print this data nicely.


    # >>> The beginning of the program.
    def beginProgram(self):

        menuChoices = ("Calculate pay cheque","View month data","Import a new csv file","Edit pay data", "Overall statistics")
        choice = self.mO.mainMenu(menuChoices) # Get a choice from the main menu.

        # >>> What now after choice?
        match choice:
            case '1': # "1) Calculate pay cheque."
                try:
                    tableNames = self.dM.getTableNames() # Get the names of all the tables.
                    # tableNames.pop()
                    tableName = self.mO.choosePayCheque(tableNames, self.CURRENT_YEAR, self.CURRENT_MONTH, self.CURRENT_DAY) # Choose the month to calculate.
                    if tableName == "quit": return # If the user wants to quit, we quit.
                    while True: # Repeat until broken.
                        previousMonthTableIndex = tableNames.index(tableName) + 1 # Get the index of the previous month.
                        previousMonthTableName = tableNames[previousMonthTableIndex] # Get the previous month table name.
                        self.calculatePayChequeChoice(previousMonthTableName, tableName, True) # Run choice function.
                        if ( tableNames.index(tableName) == 0 ): # If we are at index ZERO,
                            print("\nFurthest recorded pay cheque.") # tell the user.
                        elif ( tableNames.index(previousMonthTableName) == (len(tableNames) - 1) ): # If we are at the last index,
                            print("\nEarliest recorded pay cheque.") # tell the user.
                        shiftPayChequeCheck = input("\nWASD? ").upper() # See whether the user wants to an adjacent pay cheque.
                        if  ( ( shiftPayChequeCheck == 'W' ) or ( shiftPayChequeCheck == 'D' ) ): # If the user enters W or D,
                            if ( tableNames.index(tableName) != 0 ): # and we are not at index ZERO,
                                tableName = tableNames[tableNames.index(tableName)-1] # view next month.
                        elif ( shiftPayChequeCheck == 'A' ) or ( shiftPayChequeCheck == 'S' ) : # If the user enters A or S,
                            if ( tableNames.index(previousMonthTableName) != (len(tableNames) - 1) ): # and we are not at the last index,
                                tableName =  tableNames[tableNames.index(tableName)+1] # view previous month.
                        else: return # Else return to the main program.
                except Exception as e:
                    self.mO.printErrorDetails(e, menuChoices[int(choice)-1]) # Print the custom error message.

            case '2': # "2) View month data."
                try:
                    self.viewMonthDataChoice() # Run choice function.
                except Exception as e:
                    self.mO.printErrorDetails(e, menuChoices[int(choice)-1]) # Print the custom error message.

            case '3': # "3) Import a new CSV file."
                try:
                    self.importANewCSVFileChoice() # Run choice function.
                except Exception as e:
                    self.mO.printErrorDetails(e, menuChoices[int(choice)-1]) # Print the custom error message.

            case '4': # "4) Edit pay data."
                try:
                    self.editPayDataChoice() # Run choice function.
                except Exception as e:
                    self.mO.printErrorDetails(e, menuChoices[int(choice)-1]) # Print the custom error message.
                    
            case '5': # "5) Overall statistics."
                try:
                    self.showOverallStatistics() # Run choice function.
                except Exception as e:
                    self.mO.printErrorDetails(e, menuChoices[int(choice)-1]) # Print the custom error message.

            case 'Q': # "Q) Quit."
                self.mO.quitProgram() # Then quit the program.

                tableNames = self.dM.getTableNames() # Get the names of all the tables.
                allTablesData = self.dM.getAllData(tableNames) # Get all of the data.
                self.cM.exportAllData(allTablesData) # Export all csv data.
                self.showDashboard(False) # Export the dashboard in case of changes.

                # >>> Check whether to run the shortcuts file.
                try:
                    NEW_MD5 = self.dM.hashFile() # Save the new MD5 for the database.
                    if self.ORIGINAL_MD5 != NEW_MD5: # If the MD5s are different.
                        os.system("shortcuts run Add\ Shifts\ to\ Calendar &") # Run the shortcut to a add the shifts to the calendar.
                        print("Adding new shifts to calendar.")
                        print("Exporting paycheque dashboard.")
                except Exception as e:
                    print("Failed to add shifts to calendar,\nplease do this manually.")
                    
                # >>> Export Paycheques.
                for tableName in tableNames:
                    try: # Try to get and export the 
                        previousMonthTableIndex = tableNames.index(tableName) + 1 # Get the index of the previous month.
                        previousMonthTableName = tableNames[previousMonthTableIndex] # Get the previous month table name.
                        payChequeValue = self.calculatePayChequeChoice(previousMonthTableName, tableName, False) # Run choice function.
                        nextPaymentDate, payChequeFormatted = self.mO.dashboard(payChequeValue, False) # Launch the dashboard, and get the dashboard data.
                        self.cM.exportPaychequeData(nextPaymentDate, payChequeFormatted) # Export the paycheque data.
                    except:
                        break

                self.continueProgram = False

            case _: # In case of invalid input.
                print("\n\n! >>> ERROR - Invalid Input.\n\n") # Print an error warning.
                self.mO.quitProgram() # Then quit the program.
                self.continueProgram = False


# ! - \/ \/ \/ \/ \/ - ! #
# ! - - -  Main  - - - ! #
if __name__ == "__main__":

    initMain = Main()
    initMain.showDashboard(True) # Show the dashboard at the very start.

    while initMain.continueProgram: # Loop until we want to exit.
        input("\nPress Enter to continue...") # Wait for user to be ready to continue.
        initMain.beginProgram() # Run the menu on repeat.

    initMain.dM.connection.close() # Close the database connection.
