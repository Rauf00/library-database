import sqlite3
from datetime import datetime
from datetime import timedelta

#Program is set in a way where you are a member (user) of a library.

commandList = '0. List all items in the library\n'\
              '1. Find an item in the library\n'\
              '2. Borrow an item from the libary\n'\
              '3. Return an item to the library\n'\
              '4. Donate an item to the library\n'\
              '5. List all events in the library\n'\
              '6. Find an event in the library\n'\
              '7. Register for an event in the library\n'\
              '8. Register to be a member in the library\n'\
              '9. Sign up to volunteer for the library\n'\
              '10. Ask for help\n'\
              '11. Exit program\n'\
              'If you would like to access admin privileges, please type the password! (12345678)\n'\
              '\nWhat would you like to do (0-11): '

#To access admin privileges please input 12345678!
#Only admins can list all members, volunteers and the help queries as this is hidden from users (security purposes)

adminCommandList = '0. List all members of the library\n'\
                   '1. List all volunteers for the library\n'\
                   '2. List all help queries\n'\
                   '3. Add event\n'\
                   '4. Exit admin privileges\n'\
                   '\nWhat would you like to do (0-4): '

def getCurrentDate():
    currentDate = datetime.now()
    currentYear = str(currentDate.year)
    if(len(str(currentDate.month)) == 1):
        currentMonth = "0" + str(currentDate.month)
    else:
        currentMonth = str(currentDate.month)
    if(len(str(currentDate.day)) == 1):
        currentDay = "0" + str(currentDate.day)
    else:
        currentDay = str(currentDate.day)
    currentDate = int(currentYear+currentMonth+currentDay)
    return currentDate

def getDueDate():
    currentDate = datetime.now()
    add2weeks = currentDate + timedelta(days=14)
    dueYear = str(add2weeks.year)
    if(len(str(add2weeks.month)) == 1):
        dueMonth = "0" + str(add2weeks.month)
    else:
        dueMonth = str(add2weeks.month)
    if(len(str(add2weeks.day)) == 1):
        dueDay = "0" + str(add2weeks.day)
    else:
        dueDay = str(add2weeks.day)
    dueDate = int(dueYear+dueMonth+dueDay)
    return dueDate

def listAllItems():
    conn = sqlite3.connect('library.db')
    with conn:
        cur = conn.cursor()
        query = "SELECT * FROM Item"
        cur.execute(query)
        rows=cur.fetchall()
        if rows:
            print("List of all the items in the library:\n")
        else:
            print("Sorry our library is empty :(\n")
        for row in rows:
            print("itemID: " + str(row[0]))
            print("Title: " + row[1])
            print("Type: " + row[2])
            if row[3] == 1:
                print("Available: Yes")
            else:
                print("Available: No")
            print()
    if conn:
        conn.close()

def findItem():
    conn = sqlite3.connect('library.db')
    inputItemID = input("Enter item ID: ")
    with conn:
        cur = conn.cursor()
        query = "SELECT * FROM Item WHERE itemID=:findItemID"
        cur.execute(query,{"findItemID":inputItemID})
        rows=cur.fetchall()
        if rows:
            print("We do have an item with the following ID: " + inputItemID + "\n")
        else:
            print("Unfortunately, we do not have any items with ID " + inputItemID + "\n")
        for row in rows:
            print("itemID: " + str(row[0]))
            print("Title: " + row[1])
            print("Type: " + row[2])
            if row[3] == 1:
                print("Available: Yes")
            else:
                print("Available: No")
        print()
    if conn:
        conn.close()

def isAvailable(inputItemID):
    conn = sqlite3.connect('library.db')
    conn.row_factory = lambda cursor, row: row[0]
    result = False
    with conn:
        cur = conn.cursor()
        query = "SELECT available FROM Item WHERE itemID=:inputItemID"
        cur.execute(query, {"inputItemID":inputItemID})
        rows = cur.fetchall()
        if(rows[0]==1):
            result = True
        else:
            result = False
    if conn:
        conn.close()
    return result

def borrowItem():
    conn = sqlite3.connect('library.db')
    inputPersonID = int(input("Enter your library ID: "))
    inputItemID = int(input("Enter item ID: "))
    if(isAvailable(inputItemID) == False):
        print("\nItem is not available to be borrowed at the moment\n")
        if conn:
            conn.close()
        return
    inputIssueDate = getCurrentDate()
    inputDueDate = getDueDate()
    dueYear = str(inputDueDate)[:4]
    dueMonth = str(inputDueDate)[4:-2]
    dueDay = str(inputDueDate)[6:]
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = "INSERT INTO BorrowedAndReturned(itemID, pid, issueDate, dueDate) VALUES (:itemID, :pid, :issueDate, :dueDate)"
        try:
            cur.execute(query,{"itemID":inputItemID, "pid":inputPersonID, "issueDate":inputIssueDate, "dueDate":inputDueDate})
            print("You've borrowed the item! Your due date is: " + dueYear + "-" + dueMonth + "-" + dueDay + "\n")
        except sqlite3.IntegrityError:
            print("ERROR: There was a problem borrowing the item\n")
    if conn:
        conn.close()

def donateItem():
    conn = sqlite3.connect('library.db')
    itemID = int(input("Enter item ID: "))
    itemTitle = input("Enter item title: ")
    itemType = input("Enter item type: ")
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = "INSERT INTO Item(itemID, title, type) VALUES (:newItemID, :newItemTitle, :newItemType)"
        try:
            cur.execute(query,{"newItemID":itemID, "newItemTitle":itemTitle, "newItemType":itemType})
            print("The item was added!\n")
        except sqlite3.IntegrityError:
            print("ERROR: There was a problem adding your item to the database!\n")
    if conn:
        conn.close()

def returnItem():
    conn = sqlite3.connect('library.db')
    inputPersonID = int(input("Enter your library ID: "))
    inputItemID = int(input("Enter item ID: "))

    #RETURN DATE WILL GET THE CURRENT DATE, SO TO TEST FOR RETURNING ITEMS PAST THE DUE DATE (WHERE MEMBERS RECIEVE FINES),
    #PLEASE CHANGE THE getCurrentDate() to getDueDate()+2;
    #THIS WAY THE RETURN DATE IS PAST THE DUE DATE
    #WE IMPLEMENTED OUR FUNCTION TO GET CURRENT DATE SO USERS HAVE AN AUTHENTIC FEATURE IN RETURNING ITEMS AND THE DATE IS HANDLED AUTOMATICALLY BY THE PROGRAM.
    inputReturnDate = getCurrentDate()

    conn.row_factory = lambda cursor, row: row[0]
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        queryUpdate = "UPDATE BorrowedAndReturned SET returnDate =:itemReturnDate WHERE (itemID=:findItemID AND pid=:findPersonID)"
        cur.execute(queryUpdate,{"itemReturnDate":inputReturnDate, "findItemID":inputItemID, "findPersonID":inputPersonID})
        if cur.rowcount == 0:
            print("ERROR: The book was borrowed by another person or wrong item ID was typed!\n")
        else:
            print("\nAn item is returned!\n")
            queryGetDueDate = "SELECT dueDate FROM BorrowedAndReturned WHERE itemID=:findItemID AND pid=:findPersonID"
            cur.execute(queryGetDueDate, {"findItemID":inputItemID, "findPersonID":inputPersonID})
            rows = cur.fetchall()
            dueDate = rows[0]
            if(inputReturnDate > dueDate):
                queryGetOldFines = "SELECT fines FROM Person WHERE pid=:findPersonID"
                cur.execute(queryGetOldFines, {"findPersonID":inputPersonID})
                rows = cur.fetchall()
                newFine = rows[0] + 10
                queryFinePerson = "UPDATE Person SET fines = :updateFine WHERE pid=:findPersonID"
                cur.execute(queryFinePerson, {"updateFine": newFine,"findPersonID":inputPersonID})
                print("Due date has been passed! You were fined 10$\n")
    if conn:
        conn.close()

def listAllEvents():
    conn = sqlite3.connect('library.db')
    with conn:
        cur = conn.cursor()
        query = "SELECT * FROM Event"
        cur.execute(query)
        rows=cur.fetchall()
        if rows:
            print("List of all the events at the library:\n")
        else:
            print("Sorry our library is not hosting any events at the moment:(\n")
        for row in rows:
            print("eventID: " + str(row[0]))
            print("Name: " + row[1])
            print("Preference: " + row[2])
            print("Cost: " + str(row[3]))
            print()
    if conn:
        conn.close()

def addEvent():
    conn = sqlite3.connect('library.db')
    conn.row_factory = lambda cursor, row: row[0]
    inputID = int(input("Enter event ID: "))
    inputName = input("Enter name of the event: ")
    inputAudience = input("Enter the target audience: ")
    inputCost = int(input("Enter the cost: "))
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = 'INSERT INTO Event VALUES (:getID, :getName, :getAudience, :getCost)'
        try:
            cur.execute(query, {"getID":inputID, "getName":inputName, "getAudience":inputAudience, "getCost":inputCost})
            print("The event is created!\n")
        except sqlite3.IntegrityError:
            print("ERROR: the event with this ID already exists or wrong values are given!\n")
    if conn:
        conn.close()
        
def findEvent():
    conn = sqlite3.connect('library.db')
    inputEventID = input("Enter event ID: ")
    with conn:
        cur = conn.cursor()
        query = "SELECT * FROM Event WHERE eventID=:findEventID"
        cur.execute(query,{"findEventID":inputEventID})
        rows=cur.fetchall()
        if rows:
            print("We do have an event with the following ID: " + inputEventID + "\n")
        else:
            print("Unfortunately, we do not have any events with ID " + inputEventID + "\n")
        for row in rows:
            print("eventID: " + str(row[0]))
            print("Name: " + row[1])
            print("Preference: " + row[2])
            print("Cost: " + str(row[3]))
            print()
    if conn:
        conn.close()

def registerEvent():
    conn = sqlite3.connect('library.db')
    inputPersonID = int(input("Enter your library ID: "))
    inputEventID = int(input("Enter event ID: "))
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = "INSERT INTO Attending(pid, eventID) VALUES (:findPersonID, :findEventID)"
        try:
            cur.execute(query,{"findPersonID":inputPersonID, "findEventID":inputEventID})
            print("You've registered to the event with ID " + str(inputEventID) + "\n")
        except sqlite3.IntegrityError:
            print("ERROR: Either you've already registered to the event or there is no record with given libraryID/eventID in the database\n")
    if conn:
        conn.close()

def listAllPeople():
    conn = sqlite3.connect('library.db')
    with conn:
        cur = conn.cursor()
        query = "SELECT * FROM Person"
        cur.execute(query)
        rows=cur.fetchall()
        if rows:
            print("List of all people registered in the library:\n")
        else:
            print("Unfortunately, we do not have any people")
        for row in rows:
            print("Library ID: " + str(row[0]))
            print("First name: " + row[1])
            print("Last name: " + row[2])
            print("Preference: " + row[3])
            print("Fines: " + str(row[4]))
            print()
    if conn:
        conn.close()

def signPerson():
    conn = sqlite3.connect('library.db')
    conn.row_factory = lambda cursor, row: row[0]
    inputPersonID = int(input("Enter your library ID: "))
    inputFName = input("Enter your first name: ")
    inputLName = input("Enter your last name: ")
    inputPreference = input("Enter your preference for events: ")
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = 'INSERT INTO Person(pid, firstName, lastName, preference) VALUES (:getPersonID, :getFName, :getLName, :getPreference)'
        try:
            cur.execute(query, {"getPersonID":inputPersonID, "getFName":inputFName, "getLName":inputLName, "getPreference":inputPreference})
            print("You've registered to the library with personal ID " + str(inputPersonID) + "\n")
        except sqlite3.IntegrityError:
            print("ERROR: The ID is alredy taken! Choose another ID\n")
    if conn:
        conn.close()

def listAllVolunteers():
    conn = sqlite3.connect('library.db')
    with conn:
        cur = conn.cursor()
        query = "SELECT Personnel.pid, firstName, lastName, preference FROM Personnel JOIN Person ON Personnel.pid=Person.pid"
        cur.execute(query)
        rows=cur.fetchall()
        if rows:
            print("List of all volunteers in the library:\n")
        else:
            print("Unfortunately, we do not have any volunteers")
        for row in rows:
            print("ID: " + str(row[0]))
            print("First name: " + row[1])
            print("Last name: " + row[2])
            print("Preference: " + row[3])
            print()
    if conn:
        conn.close()

def signVolunteer():
    conn = sqlite3.connect('library.db')
    conn.row_factory = lambda cursor, row: row[0]
    inputPersonID = int(input("Enter your library ID: "))
    position = "volunteer"
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        query = 'INSERT INTO Personnel VALUES (:getPersonID, :getPosition)'
        try:
            cur.execute(query, {"getPersonID":inputPersonID, "getPosition":position})
            queryName = 'SELECT firstName FROM Person WHERE pid = :getPersonID'
            cur.execute(queryName, {"getPersonID":inputPersonID})
            rows = cur.fetchall()
            print("Welcome to our team, " + rows[0] + "!")
            print("Your position is: Volunteer\n")
        except sqlite3.IntegrityError:
            print("ERROR: Either you've already signed up or you are not a memeber of the library!\n")
    if conn:
        conn.close()

def askForHelp():
    conn = sqlite3.connect('library.db')
    inputHelpID = int(input("Enter the help ID: "))
    inputPersonID = int(input("Enter your library ID: "))
    userQuestion = input("Please write down what you need help with:\n")
    with conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        insertHelpQuery = "INSERT INTO Help(hid, text) VALUES (:findHelpID, :findText)"
        insertRequestQuery = "INSERT INTO Request VALUES (:findPersonID, :findHelpID)"
        try:
            cur.execute(insertHelpQuery, {"findHelpID":inputHelpID, "findText":userQuestion})
            cur.execute(insertRequestQuery, {"findPersonID":inputPersonID, "findHelpID":inputHelpID})
            print("You've added a question with ID " + str(inputHelpID) + "\n")
        except sqlite3.IntegrityError:
            print("ERROR: The question with this ID already exists or you are not a member of the library!\n")
    if conn:
        conn.close()

def listAllHelp():
    conn = sqlite3.connect('library.db')
    with conn:
        cur = conn.cursor()
        query = "SELECT Help.hid, Request.pid, Help.text FROM Help JOIN Request ON Help.hid=Request.hid"
        cur.execute(query)
        rows=cur.fetchall()
        if rows:
            print("List of all help queries:\n")
        else:
            print("Unfortunately, we do not have any questions at the moment\n")
        for row in rows:
            print("Help ID: " + str(row[0]))
            print("Person ID: " + str(row[1]))
            print("Text: " + row[2])
            print()
    if conn:
        conn.close()

def main():
    print("Welcome to the Library Database")
    userInput = int(input(commandList))
    while userInput != 13:
        if userInput==0:
            listAllItems()
            userInput=int(input(commandList))
        elif userInput==1:
            findItem()
            userInput=int(input(commandList))
        elif userInput==2:
            borrowItem()
            userInput = int(input(commandList))
        elif userInput==3:
            returnItem()
            userInput=int(input(commandList))
        elif userInput==4:
            donateItem()
            userInput=int(input(commandList))
        elif userInput==5:
            listAllEvents()
            userInput = int(input(commandList))
        elif userInput==6:
            findEvent()
            userInput = int(input(commandList))
        elif userInput==7:
            registerEvent()
            userInput = int(input(commandList))
        elif userInput==8:
            signPerson()
            userInput = int(input(commandList))
        elif userInput==9:
            signVolunteer()
            userInput = int(input(commandList))
        elif userInput==10:
            askForHelp()
            userInput = int(input(commandList))
        elif userInput==11:
            break
        elif userInput==12345678:
            adminInput = int(input(adminCommandList))
            while(adminInput!=4):
                if adminInput==0:
                    listAllPeople()
                    adminInput = int(input(adminCommandList))
                elif adminInput==1:
                    listAllVolunteers()
                    adminInput = int(input(adminCommandList))
                elif adminInput==2:
                    listAllHelp()
                    adminInput = int(input(adminCommandList))
                elif adminInput==3:
                    addEvent()
                    adminInput = int(input(adminCommandList))
                elif adminInput==4:
                    break
                else:
                    print("Invalid option. Please choose again from the following options:")
                    adminInput = int(input(adminCommandList))
            userInput = int(input(commandList))
        else:
            print("Invalid option. Please choose again from the following options:")
            userInput=int(input(commandList))

main()