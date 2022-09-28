# To be run by Shortcuts, not by me.

import sys
from datetime import date
from CsvManagement import CsvManagement
from DatabaseManagement import DatabaseManagement


# ! - Classes - ! #
cM = CsvManagement()
dM = DatabaseManagement()


# ! - Constants - ! #
CURRENT_YEAR  = str(date.today().year) # Set the current year.
CURRENT_MONTH = str(date.today().month) # Set the current month.
CURRENT_DAY   = str(date.today().day) # Set the current day.


# >>> Check if a file was passed as an argument.
try:
	cM.CSV_FILE = sys.argv[1] # Set the csv file to the command-line argument.
except Exception as e:
	print("No argument was passed to the main python file execution.") # Tell the user what went wrong.
	quit() # Quit.


# >>> Import the csv file.
cM.clearArrays() # Clear all of the arrays.
cM.getCSVData() # Get the data from the csv file.
cM.processCSVData() # Save the data from the csv file
cM.combineData() # Combine the data into one 2D array.
dM.saveData(cM.dataArray, CURRENT_YEAR, CURRENT_MONTH) # Save the data from the 2D array to the database.



# >>> Export all the data.
tableNames = self.dM.getTableNames() # Get the names of all the tables.
allTablesData = self.dM.getAllData(tableNames) # Get all of the data.
self.cM.exportAllData(allTablesData, tableNames)



# >>> Close the connection with the DB.
dM.connection.close()




# Try get shortcuts to run this, see if it works.
# Maybe automatically run the 'add to calendar' shortcut after?

# Try automate this whenever I get an email about a shift change.
# For it to work, gotta find a way to get the csv off of the website :/


# ALSO: stop passing variables, just use cM.asdf instead, works better, more efficient.
# Go through and do this at some point (make a backup just in case lol).
