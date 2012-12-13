import MySQLdb as mdb

#setting up MySQLdb was a horrible experience on the Mac !!  Most of the internet seemed to be complaining about the errors in 
#the configuration files :)  

from datetime import datetime
import sys

#############################################################################################################
#  A simple terminal based To Do List using strong Model View Controller to separate out the various elements
#  As this is decoupled the view could be from another source such as web or mobile, 
#  with just a few additions to the controller class
#  The Controller is a simple bridge from the view to the Model and back again
#  The model uses MySQLdb for data persistency.
#############################################################################################################


class ToDoModel(object):
	"""
  ToDoModel handles all database transactions
  
	"""
	def __init__(self):
		
		#initialiser checks for presence of database and table
		#creating them if not present.  Not a secure database as you can see
		
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		try:
			sql = 'CREATE DATABASE todo'
			cursor.execute(sql)
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))	
		try:
			sql = "USE todo"
			cursor.execute(sql)
			sql = "CREATE TABLE todolist (TEXT VARCHAR(50), DATECREATED TIMESTAMP DEFAULT NOW() , COMPLETED INT)"
			cursor.execute(sql)
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
		
	def get_list(self,sort_type,filter_type):
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)
		
		#depending on the values of sort_type and filter_type we will filter for 
		#completed/uncompleted and order alphabetically or in date order
		#otherwise list all
						
		if sort_type==1 and filter_type ==0:
			sql = "SELECT * FROM todolist"
		elif sort_type==0 and filter_type ==1:  #filter type 1 means we want only completed items, 0 sort is alphabetically
			sql = "SELECT * FROM todolist WHERE COMPLETED = '1' ORDER by TEXT" 
		elif sort_type==0 and filter_type ==2:  #filter type 2 means we want only uncompleted items
			sql = "SELECT * FROM todolist WHERE COMPLETED = '0' ORDER by TEXT"
		elif sort_type==1 and filter_type ==1:  #sort by date and filter for completed items
			sql = "SELECT * FROM todolist WHERE COMPLETED = '1' ORDER by DATECREATED"
		elif sort_type==1 and filter_type ==2:  #filter type 2 means we want only uncompleted items
			sql = "SELECT * FROM todolist WHERE COMPLETED = '0' ORDER by DATECREATED"
		else:
			sql = "SELECT * FROM todolist ORDER by TEXT"
		try:
			cursor.execute(sql)
			results = cursor.fetchall()
			return results
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
					
		
	def insert(self,text):
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)		
		sql = "INSERT INTO todolist (TEXT,COMPLETED) VALUES ('%s', '%d' )" %  (text, 0,)
		try:
			cursor.execute(sql)
			db.commit()
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))

			db.rollback()
		db.close()

	def update(self,newtext,item):
		#I pass around the 'item' from various methods, here I'm using the 'datecreated' as the key
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)		
		sql = "UPDATE todolist SET TEXT = '%s' WHERE DATECREATED = '%s'" % (newtext,item[1])
		try:
			cursor.execute(sql)
			db.commit()
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
			db.rollback()
		db.close()
		
	def complete(self,item):
		#to improve on the code I would probably combine the update and complete methods into something more abstract
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)
		new_status = 1
		if item[2]:
			new_status = 0		
		sql = "UPDATE todolist SET COMPLETED = '%d' WHERE DATECREATED = '%s'" % (new_status,item[1])
		try:
			cursor.execute(sql)
			db.commit()
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
			db.rollback()
		db.close()
				
	def delete(self,item):
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)		
		sql = "DELETE FROM todolist WHERE DATECREATED = '%s'" % item[1]
		try:
			cursor.execute(sql)
			db.commit()
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
			db.rollback()
		db.close()
		
	def purge(self):
		db = mdb.connect(host="localhost",user="root")
		cursor = db.cursor()
		sql = "USE todo"
		cursor.execute(sql)		
		sql = "DELETE FROM todolist"
		try:
			cursor.execute(sql)
			db.commit()
		except db.Error, e:
			sys.stderr.write("[ERROR] %d: %s\n" % (e.args[0], e.args[1]))
			db.rollback()
		db.close()

	def close(self):
		pass			



class ToDoListController(object):
	"""
  ToDoListController class directs instructions to the ToDoModel class and communicates with the ToDoView input and output
  
	"""
	def __init__(self):
		self.model = ToDoModel()
		self.view = ToDoView(self)
		self.return_list(0,0)
		
	def return_to_do(self,key): #return a single to do
		#I would improve the code by ensuring the view calls back to the controller where appropriate
		#even to return single to_do items (though this currently does reduce calls on the database)
		pass
		
	def return_list(self,sort_type,filter_type): 
		#this will return a sorted list depending on the sort and filter type requested
		list = self.model.get_list(sort_type,filter_type)
		self.view.main_list(sort_type,filter_type,list)
  
	def insert_to_do(self,text): 
		self.model.insert(text)
		list = self.model.get_list(0,0)
		self.view.main_list(0,0,list)		
		
	def delete_all(self): 
		self.model.purge()	
		self.model.get_list(0,0) #d'oh this should be 'return_list' method ... not this imaginary one!!

	def delete_item(self,item): 
		self.model.delete(item)	
		self.return_list(0,0)		

	def edit_item(self,text,item): 
		self.model.update(text,item)	
		self.return_list(0,0)		

	def complete(self,item): 
		self.model.complete(item)	
		self.return_list(0,0)	
		

class ToDoView(object):
	"""
  The ToDoView class deals with all the on screen presentations and keyboard inputs, communicating with the ToDoListController.
  
	"""
	def __init__(self,controller):
		self.title = "To Do List"
		self.controller = controller	
		
	def main_list(self,sort_type,filter_type,list):
		print "\n____TO DO LIST_______________________________________\n"
		i=1
		for result in list:
			print "%s [%d]  %s  %s" % (format_completed(result[2]),i,result[1].strftime("%a %d %b %H:%M"),result[0])
			i +=1
		if not len(list):
			print "\nHIT ENTER TO ADD A TO DO ITEM"		
		print "\n_____________________________________________________\n"
		print "[Number] to select a to do item e.g. '3' "
		print "[C] to show completed items"
		print "[U] for uncompleted"
		print "[L] to list all items"
		print "[A] to list alphabetically"
		print "[O] to show in date order"
		print "[P] to purge the list"
		print "Any other key to add a new to do item or [X] to Exit"
		var = raw_input("\nEnter Selection: ")
		
		#Here I use the array of results against the numbering on the fly
		#calling the appropriate item from the list and passing to the single_to_do view method
		try:
			if int(var)<=len(list):
				self.view_single_to_do(list[int(var)-1])
			else:
				self.add_to_do()		
		except:		
			#process the various menu options, calling the appropriate method via the controller
			if var == "T":
				pass
			elif var == "P":
				self.purge_list()
			elif var == "C":
				self.controller.return_list(sort_type,1)
			elif var == "U":
				self.controller.return_list(sort_type,2)
			elif var == "L":
				self.controller.return_list(0,0)
			elif var == "A":
				self.controller.return_list(0,filter_type)	
			elif var == "O":
				self.controller.return_list(1,filter_type)											
			elif var == "X":
				pass
			else:
				self.add_to_do()		
		
	def view_single_to_do(self,item):
		print "\n_____________________________________________________\n"
		print "%s %s  %s" % (format_completed(item[2]),item[1].strftime("%a %d %b %H:%M"),item[0])
		print "\n_____________________________________________________"
		print "\n[E] to edit this item"
		print "[C] to toggle completion state"
		print "[D] to delete the item"
		print "Any other key to return to main menu or [X] to Exit"
		var = raw_input("\nEnter Selection: ")
		print "you entered ", var		

		if var == "E":
			self.edit_to_do(item)
		elif var == "D":
			self.controller.delete_item(item)
		elif var == "C":
			self.controller.complete(item)			
		elif var == "X":
			pass
		else:
			self.controller.return_list(0,0)
		
	def add_to_do(self):
		var = raw_input("Enter new to do text: ")
		if len(var):
			self.controller.insert_to_do(var)	
		else:
			self.controller.return_list(0,0)
							
	def edit_to_do(self,result):
		print "\n___________________EDIT____________________________\n"
		print "%s %s  %s" % (format_completed(result[2]),result[1].strftime("%a %d %b %H:%M"),result[0])
		print "\n_____________________________________________________"

		var = raw_input("\nEnter new text for this to do (or hit enter to cancel): ")

		if len(var):
			self.controller.edit_item(var,result)	
		else:
			self.controller.return_list(0,0)

	def purge_list(self):
		var = raw_input("\nIf you are sure you want to purge the list enter 'Y', any other key to cancel: ")
		if var == "Y":
			self.controller.delete_all()
		else:
			self.controller.return_list(0,0)	


#this is a simple helper function to format the completion integer with something more visual		

def format_completed(integer):
	if integer:
		return "X"
	else:
		return " "	
	
# this is the actual code being called when we begin, the Controller instantiates both the Model and the View
# and calls up the main menu method
		
controller = ToDoListController()


#improvements would be to check for characters that need escaping e.g. ' etc.

