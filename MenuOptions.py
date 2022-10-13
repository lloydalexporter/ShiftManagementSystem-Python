#!/usr/bin/env python3


# ! - Libraries - ! #
import calendar
import pandas as pd
import datetime as dt
from pprint import pprint as pp
from decimal import Decimal
from os import system


class MenuOptions:
	
	# ! - Functions - ! #
	def __init__(self): # Always run.
		self.ifMain = False # Initialise and set to False.
		if __name__ == "__main__": self.ifMain = True # If this is Main, set to True.
		
		self.payYear, self.payMonth, self.payDay = "", "", ""
		
		self.TWO_DP = Decimal(10) ** -2 # Set the number of decimal places.
		self.clear = lambda: system('clear') # Create this to clear the screen.
		
	
	# >>> Get a user input for the pay per hour amount.
	def inputNewPayPerHour(self):
		
		while True: # Loop until we get a valid user input.
			newPPH = input("\nNew Pay Per Hour: £").upper().strip() # Get user input, make it upper case.
			if newPPH == 'Q': return "quit" # Return with quit.
			try:
				newPPH = float(newPPH) # Try to make the input a float, if this is successful,
				break # break the loop.
			except:
				continue # Else continue the loop.
			
		return newPPH # Return the pay her hour.

	# >>> Get the year of the shift.
	def inputShiftYear(self): pass
	
	# >>> Get a user input from allowed inputs list.
	def getUserInput(self, validInputs, question, includeQuit):
		if len(validInputs) == 0:
			return -1
		
		while True: # Loop until we get a valid user input.
			choice = input('{} '.format(question)).upper().strip() # Get user input, make it upper case.
			if choice in validInputs: # If the user input is valid,
				break # break out of the loop.
			if (includeQuit) and (choice == 'Q'): # If we can quit, and the choice is quit,
				return "quit" # Return with quit.
		
		return choice # Return the user's choice.
	
	
	# >>> Options for which pay cheque to calculate.
	def choosePayCheque(self, tableNames, CURRENT_YEAR, CURRENT_MONTH, CURRENT_DAY):
		self.clear() # Clear the screen.
		
		self.workOutPaymentDay(CURRENT_YEAR, CURRENT_MONTH, "28") # Update class paydates.
		
		validInputs = ('1','2') # The valid inputs.
		
		# >>> Print the menu.
		print("For what month would you like to calculate?\n") # Print the question.
		print("1) Next Pay Cheque") # The most recent table.
		print("2) Other") # View other tables.
		
		choice = self.getUserInput(validInputs, "#?", True) # Get the user input.
		if choice == '1': # If the user wants the most recent pay cheque,
			if int(CURRENT_DAY) > int(self.payDay): # If the day past pay cheque day,
				CURRENT_MONTH = str(int(CURRENT_MONTH) + 1) # set the month to next month.
			if len(CURRENT_MONTH) == 1: # If the current month is only one number in length,
				CURRENT_MONTH = '0' + CURRENT_MONTH # add the leading ZERO.
			tableName = CURRENT_YEAR + '_' + CURRENT_MONTH # Set the tableName.
		elif choice == 'quit':
			return choice
		else:
			tableName = self.chooseTableName(tableNames, "For what month would you like to calculate?\n") # Else choose from the list of table names.
		
		return tableName # Return tableName.

	
	# >>> Select a table name.
	def chooseTableName(self, tableNames, message):
		self.clear() # Clear the screen.
		
		validInputs = [ str(i+1) for i in range(len(tableNames)) ] # Set the valid inputs to the indexes of table names, plus one.
		
		# >>> Print the menu.
		print(message) # Print the question.
		for x in range(len(validInputs)): # For every valid input,
			print("%d) %s" % (x+1, tableNames[x])) # print a row.
		
		choice = self.getUserInput(validInputs, "#?", True) # Get user input.
		if choice == 'quit': return "quit"
			
		tableName = tableNames[int(choice)-1] # Get the corresponding table name.
		
		return tableName # Return the table name.
	
	
	# >>> Print month data.
	def printMonthData(self, tableName, monthData):
		self.clear() # Clear the screen.
		
		workingHours = 0 # Initialise the working hours sum.
		
		print("Data from %s table:" % tableName) # Print the header.
		print("\nDay | Date | Start |  End  | Hours") # Print the table header
		
		for r in monthData: # For every row of monthData,
			temp = tableName.replace('_', '-') + "-" + str(r[1])
			date = pd.Timestamp(temp)
			print("%.3s | %4d | %5s | %5s | %.5g" % (date.day_name(), r[1], r[2], r[3], float(r[5]))) # print the data nicely,
			workingHours += r[5] # and add the working hours.
			
		print("\nShifts: %2d  | Working Hours: %g" % (len(monthData), workingHours)) # Print the footer.
		
		
	# >>> The main user menu.
	def mainMenu(self, menuChoices):
		self.clear() # Clear the screen.
		
		validInputs = [ str(i+1) for i in range(len(menuChoices)) ]
		
		# >>> Print the menu.
		print("Hello, would you like to:\n") # Print the header.
		for x in range(len(validInputs)): # For every valid input,
			print("%d) %s" % (x+1, menuChoices[x])) # print a row.
		print("Q) Quit") # Print the quit line.
		
		validInputs.append('Q') # Add Q.
		choice = self.getUserInput(validInputs, "#?", True) # Get user input.
		
		return choice # Return the user's choice.
	
	
	# >>> Print the error.
	def printErrorDetails(self, e, menuChoice):
		menuChoice = menuChoice.lower() # Make the choice lower.
		print("\n! >>> ERROR - Unable to %s:" % menuChoice) # Say there was an error with their choice.
		print(e) # Print the actual error.
	
	
	# >>> Print the pay cheque data.
	def printPayCheque(self, tableName, shiftCount, totalHours, payChequeValue, doPrint):
		if doPrint: self.clear() # Clear the screen.
		
		self.workOutPaymentDay(tableName[:4], tableName[5:], "28") # Update class paydates.
		
		if doPrint: print("Pay Cheque expected on", self.getPrettyDate(self.payYear, self.payMonth, self.payDay)) # Print the header.
		
		if doPrint: print("\nShifts: %d" % shiftCount) # Print some shift details.
		if doPrint: print("Working Hours: %g" % totalHours) # Print some hours details.
		
		payChequeValue = Decimal(payChequeValue).quantize(self.TWO_DP) # Round to two decimal places.
		
		if doPrint: print("Expected amount: £", payChequeValue) # Print the expected pay cheque amount.
		
		# >>> Days until pay cheque.
		today = dt.date.today()
		payChequeDate = dt.date(int(self.payYear), int(self.payMonth), int(self.payDay))
		dayDifference = (payChequeDate - today).days
#		dayDifference = str(dayDifference) + " day" if dayDifference == 1 else str(dayDifference) + " days" # Add the dynamic days text.
		if doPrint: print("Payment due in:", dayDifference)
		
		if not doPrint: return payChequeValue # Return the pay cheque value.
		
		
	# >>> Date to day of the year.
	def date2doy(self, year, month, day):
		
		dateFormat = "%d-%02d-%02d" % (int(year), int(month), int(day)) # Format the date.
		date = dt.datetime.strptime(dateFormat, '%Y-%m-%d') # Set as date object.
		dayOfYear = date.strftime('%j') # Get the day of the year from the date.
		
		return dayOfYear # Return the day of the year.
	
	
	# >>> Date to day of the year.
	def doy2date(self, year, doy):
		
		formatString = str(year) + ' ' + str(doy) # Format the year and day of the year.
		date = dt.datetime.strptime(formatString, '%Y %j') # Set the day of year as a date object.
		
		return str(date)[:4], str(date)[5:7], str(date)[8:10] # Return the date in three seperate parts: Y, M, D.
	
	
	# >>> Subtract one day to the date.
	def subtractOneDay(self, year, month, day):
		
		doy = int(self.date2doy(year, month, day)) # Get the date as the day of the year.
		doy -= 1 # Subtract one day.
		
		return self.doy2date(year, doy) # Return the output of converting the day of the year into a date.
	
	
	# >>> Work out the next payment day.
	def workOutPaymentDay(self, payYear, payMonth, payDay):
		
		self.payYear, self.payMonth, self.payDay = payYear, payMonth, payDay # Set to class values.
		
		while True: # Loop until we get a weekday.
			nextPayDay = calendar.weekday(int(self.payYear), int(self.payMonth), int(self.payDay)) # Get the weekday from date.
			if nextPayDay in [0,1,2,3,4]: break # If the next payment day is a week day, break from loop.
			# If we don't break, then it is a weekend.
			self.payYear, self.payMonth, self.payDay = self.subtractOneDay(self.payYear, self.payMonth, self.payDay) # Subtract one day too the payment date, set to global variables.
		
		
	# >>> Return text of a pretty date.
	def getPrettyDate(self, year, month, day):
		
		dateFormat = "%d-%02d-%02d" % (int(year), int(month), int(day)) # Format the date.
		date = dt.datetime.strptime(dateFormat, '%Y-%m-%d') # Set as date object.
		dayOfWeek = date.strftime('%a')
		monthName = date.strftime('%b')
		
		fullDate = "%s-%s-%s-%s" % (dayOfWeek, day, monthName, year)
		
		return fullDate
		
		
	# >>> Print the dashboard with all the quick data.
	def dashboard(self, payChequeValue):
		self.clear() # Clear the screen.
		
		# >>> Print title header.
		print("Shift Management System")
		print("–––––––––––––––––––––––")
		
		# >>> Next payment date.
		print("Next Payment Due:\n%23s" % self.getPrettyDate(self.payYear, self.payMonth, self.payDay))
		
		# >>> Next pay cheque amount.
		payChequeFormatted = "£ " + str(Decimal(payChequeValue).quantize(self.TWO_DP))
		print("Next Pay Cheque:\n%23s" % payChequeFormatted)
		
		# >>> Days until pay cheque.
		today = dt.date.today()
		payChequeDate = dt.date(int(self.payYear), int(self.payMonth), int(self.payDay))
		dayDifference = (payChequeDate - today).days
		dayDifference = str(dayDifference) + " day" if dayDifference == 1 else str(dayDifference) + " days" # Add the dynamic days text.
		print("Payment due in:\n%23s" % dayDifference)
		
		# >>> Print the footer.
		print("–––––––––––––––––––––––")
		
	
	# >>> Program quitting screen.
	def quitProgram(self):
		print("\nQuitting the program...")
		