from flask import Flask, request
from flask_restful import Api
import mysql.connector

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Working" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed 

@application.route("/users", methods = ["POST", "GET"])
# route to modify the 'users' table
def updateUsers():
    if request.method == "POST":
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database
        mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES ('WAs','sad','qdd','EDD','Sss')"
        #query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES (request.form["accountID"], request.form["firstName"], request.form["surname"], request.form["email"], request.form["password"])"
        mycursor.execute(query)
        #mydb.commit()
        test = (request.form["user"]).decode("utf-8"))
        return test
    elif request.method == "GET":
        return "GET"

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)
    application.run(debug=True)  # begins running the Api server


