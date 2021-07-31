from flask import Flask, request, jsonify
from flask_restful import Api
import mysql.connector
import boto3
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
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES ('%s','%s','%s','%s','%s')" % (data['accountID'], data['firstName'], data['surname'], data['email'], data['password']) # MySQL query to add the data sent with the API to the appropriate columns in the 'users' table
        myCursor.execute(query) # executes the query in the MySQL database
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success" # confirms that MySQL database was successfully updated
    except:
        return "error" # signifies that an error occured when adding the user's data in the 'users' table
        
@application.route("/verifyUser", methods = ["POST"])
# route to verify a user's sign in details
def verifyUser():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s' AND password = '%s'" % (data['email'], data['password']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = (myCursor.fetchone())[0] # returns the first result of the query result
        if result == None: # if there are no rows which match the query, then the result is 'None' and so 
            return result
        else:
            return result
    except:
        return "error"
    
@application.route("/verifyAccount", methods = ["POST"])
# route to verify that a user's account doesn't already exist
def verifyAccount():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s'" % (data['email'])
        myCursor.execute(query)
        result = (myCursor.fetchone())[0]
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
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT messageName, fileText FROM audioMessages WHERE accountID = '%s'" % (data['accountID'])
        myCursor.execute(query)
        result = myCursor.fetchall()
        result_dict = dict()
        result_dict["length"] = len(result)
        for i in result:
            result_dict[str(result.index(i))] = i
        return jsonify(result_dict)
    except:
        return "error"
    
    
@application.route("/uploadS3", methods = ["POST"])
# route to upload byte data of the user's personalised audio messages
def uploadS3(): 
    file = request.files["file"] # assigns the txt file storing the bytes of the audio message to the variable 'file'
    full_filename = os.path.join("/tmp", file.filename) # the variable 'full_filename' stores the path to where the txt file will be temporarily stored on the AWS server
    file.save(os.path.join(full_filename)) # temporarily saves the txt file in the "/tmp" folder on the AWS server
    data = request.form # assigns the metadata sent to the API to a variable ('data')
    s3 = boto3.client("s3", aws_access_key_id=data["accessKey"], aws_secret_access_key=data["secretKey"]) # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
    s3.upload_file(Filename=full_filename, Bucket=data["bucketName"], Key=data["s3File"]) # uploads the txt file to the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is stored on S3 is the 'messageID' of the audio message which is being stored as a txt file.
    return file.filename
    #return "success"
    #except:
       #return "error"
        
@application.route("/update_audioMessages", methods = ["POST"])
def update_audioMessages():
    #try:
    mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
    data = request.form # assigns the data sent to the API to a variable ('data')
    query = "INSERT INTO audioMessages (messageID, messageName, fileText, accountID) VALUES ('%s', '%s', '%s', '%s')" % (data['messageID'], data['messageName'], data['fileText'], data['accountID'])
    myCursor.execute(query)
    mydb.commit() # commits the changes to the MySQL database made by the executed query
    return "db"
        #return "success"
    #except:
        #return "error"
        
        
            

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running

