from flask import Flask, request, jsonify
from flask_restful import Api
import mysql.connector
import boto3
from werkzeug.utils import secure_filename
import os.path

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Working" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed 

@application.route("/updateUsers", methods = ["POST"])
# route to modify the 'users' table
def updateUsers():
    data = request.form 
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
        
@application.route("/verifyUser", methods = ["POST"])
# route to verify a user's sign in details
def verifyUser():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s' AND password = '%s'" % (data['email'], data['password'])
        mycursor.execute(query)
        result = (mycursor.fetchone())[0]
        if result == None:
            return "none"
        else:
            return result
    except:
        return "error"
    
@application.route("/verifyAccount", methods = ["POST"])
# route to verify that a user's account doesn't already exist
def verifyAccount():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s'" % (data['email'])
        mycursor.execute(query)
        result = (mycursor.fetchone())[0]
        if result == None:
            return "none"
        else:
            return "exists"
    except:
        return "error"
    
@application.route("/view_audioMessages", methods = ["POST"])
# route to determine how many audio messages a particular user has and what the display names are and file details are for these messages
def view_audioMessages():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT messageName, fileText FROM audioMessages WHERE accountID = '%s'" % (data['accountID'])
        mycursor.execute(query)
        result = mycursor.fetchall()
        result_dict = dict()
        result_dict["length"] = len(result)
        for i in result:
            result_dict[str(result.index(i))] = i
        return jsonify(result_dict)
    except:
        return "error"
    
    
@application.route("/uploadS3", methods = ["POST"])
# route to determine how many audio messages a particular user has and what the display names are and file details are for these messages
def uploadS3():
    #try:
    self.f = request.files["file"]
    full_filename = secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], full_filename))
    self.accessKey = request.data["accessKey"]
    self.secretKey = request.data["secretKey"]
    self.bucketName = request.data["bucketName"]
    self.s3File = request.data["s3File"]
    s3 = boto3.client("s3", aws_access_key_id=self.accessKey, aws_secret_access_key=self.secretKey)
    s3.upload_file(Filename=full_filename, Bucket=self.bucketName, Key=self.s3File)
    return "s3"
        #return "success"
    #except:
        #return "error"
        
@application.route("/update_audioMessages", methods = ["POST"])
def update_audioMessages():
    #try:
    mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
    data = request.form # assigns the data sent to the API to a variable ('data')
    query = "INSERT INTO audioMessages (messageID, messageName, fileText, accountID) VALUES ('%s', '%s', '%s', '%s')" % (data['messageID'], data['messageName'], data['fileText'], data['accountID'])
    mycursor.execute(query)
    mydb.commit() # commits the changes to the MySQL database made by the executed query
    return "db"
        #return "success"
    #except:
        #return "error"
        
        
            

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running

