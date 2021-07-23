from flask import Flask, request
from flask_restful import Api
import mysql.connector
import logging

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Working" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed 

@application.route("/users", methods = ["POST", "GET"])
# route to modify the 'users' table
def updateUsers():
    data = request.form 
    if data["method"] == "POST": # if the request from the mobile app is a 'POST' request (i.e. adding data to the 'users' table)
        try:
            mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
            mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
            data = request.form # assigns the data sent to the API to a variable ('data')
            query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES ('%s','%s','%s','%s','%s')" % (data['accountID'], data['firstName'], data['surname'], data['email'], data['password']) # MySQL query to add the data sent with the API to the appropriate columns in the 'users' table
            mycursor.execute(query) # executes the query in the MySQL database
            mydb.commit() # commits the changes to the MySQL database made by the executed query
            return "success" # confirms that MySQL database was successfully updated
        except:
            return "error" # signifies that an error occured when adding the user's data in the 'users' table
        
    elif data["method"] == "GET":
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s' AND password = '%s'" % (data['email'], data['password'])
        mycursor.execute(query)
        result = mycursor.fetchone()
        application.logging.info(result)
        if result == None:
            return "error"
        else:
            return "hello"
        
            

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running


