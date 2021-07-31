from flask import Flask, request, jsonify
from flask_restful import Api
import mysql.connector
import boto3
import pickle

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Working" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed 

@application.route("/updateUsers", methods = ["POST"])
# route to add a new user to the 'users' table 
def updateUsers():
    try:
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(data["host"]), user=(data["user"]), passwd=(data["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
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
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(data["host"]), user=(data["user"]), passwd=(data["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "SELECT accountID FROM users WHERE email = '%s' AND password = '%s'" % (data['email'], data['password']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = (myCursor.fetchone())[0] # returns the first result of the query result (accountID), if there is a result to be returned
        return result # the accountID of the account matching the details inputted by the user is returned 
    except:
        return "none" # the string 'none' is returned if the user's inputted details do not match an account stored in the 'users' MySQL table
    
@application.route("/verifyAccount", methods = ["POST"])
# route to verify that a user's account doesn't already exist
def verifyAccount():
    try:
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(data["host"]), user=(data["user"]), passwd=(data["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        query = "SELECT accountID FROM users WHERE email = '%s'" % (data['email']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = (myCursor.fetchone())[0] # returns the first result of the query result (accountID), if there is a result to be returned
        return "exists" # the string 'exists' is returned if the user's inputted details match an account which already exists in the 'users' MySQL table
    except:
        return "notExists" # the string 'notExists' is returned if the user's inputted details do not match an account which already exists in the 'users' MySQL table
    
@application.route("/view_audioMessages", methods = ["POST"])
# route to determine how many audio messages a particular user has and what the display names are and file details are for these messages
def view_audioMessages():
    try:
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(data["host"]), user=(data["user"]), passwd=(data["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        query = "SELECT messageName, fileText FROM audioMessages WHERE accountID = '%s'" % (data['accountID']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchall() # returns all the results of the query result (messageName and fileText), if there is a result to be returned
        result_dict = dict() # creates a dictionary to store the results from the executed query
        result_dict["length"] = len(result) # add the key 'length' to the dictionary to store the number of audio messages stored in the 'audioMessages' MySQL table for the concerned user
        for i in result:
            result_dict[str(result.index(i))] = i # adds the name of each audio message and the respective data from the field 'fielText' to the dictionary with keys of an incrementing numerical value 
        return jsonify(result_dict) # returns a jsonfied object of the results dictionary using the method 'jsonify'
    except:
        return "error"
    
    
@application.route("/update_audioMessages", methods = ["POST"])
# route to add data about a new audio message to the 'audioMessages' table
def update_audioMessages():
    try:
        mydb = mysql.connector.connect(host=(request.form["host"]), user=(request.form["user"]), passwd=(request.form["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)
        data = request.form # assigns the data sent to the API to a variable ('data')
        query = "INSERT INTO audioMessages (messageID, messageName, fileText, accountID) VALUES ('%s', '%s', '%s', '%s')" % (data['messageID'], data['messageName'], data['fileText'], data['accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"
    
    
@application.route("/uploadS3", methods = ["POST"])
# route to upload byte data of the user's personalised audio messages
def uploadS3(): 
    try:
        file = request.files["file"] # assigns the txt file storing the bytes of the audio message to the variable 'file'
        file.save("/tmp/audioMessage_upload.txt") # temporarily saves the txt file in the "/tmp" folder on the AWS server
        data = request.form # assigns the metadata sent to the API to a variable ('data')
        s3 = boto3.client("s3", aws_access_key_id=data["accessKey"], aws_secret_access_key=data["secretKey"]) # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
        s3.upload_file(Filename="/tmp/audioMessage_upload.txt", Bucket=data["bucketName"], Key=data["s3File"]) # uploads the txt file to the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is stored on S3 is the 'messageID' of the audio message which is being stored as a txt file.
        return "success"
    except:
        return "error"
    
@application.route("/downloadS3", methods = ["POST"])
# route to download byte data of the user's personalised audio messages
def downloadS3(): 
    #try:
    data = request.form # assigns the metadata sent to the API to a variable ('data')
    s3 = boto3.client("s3", aws_access_key_id=data["accessKey"], aws_secret_access_key=data["secretKey"]) # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
    s3.download_file(Filename="/tmp/audioMessage_download.txt", Bucket=data["bucketName"], Key=data["s3File"]) # downloads the txt file with the name equal to the concerned messageID from the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is downloaded and stored temporarily on the AWS server
    with open("/tmp/audioMessage_download.txt", 'r') as file:
        fileContent = file.read()
    return fileContent
    #return "success"
    #except:
        #return "error"
              
        
        

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running

