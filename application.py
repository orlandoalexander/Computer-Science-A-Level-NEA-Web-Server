from flask import Flask, request, jsonify, send_file
from flask_restful import Api
import mysql.connector
import boto3
import pickle
import json
import random
import string
from cryptography.fernet import Fernet

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Hey there" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed



@application.route("/updateUsers", methods = ["POST"])
# route to add a new user to the 'users' table 
def updateUsers():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]), database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES ('%s','%s','%s','%s','%s')" % (data['accountID'], data['firstName'], data['surname'], data['email'], data['password']) # MySQL query to add the data sent with the API to the appropriate columns in the 'users' table
        myCursor.execute(query) # executes the query in the MySQL database
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success"# confirms that MySQL database was successfully updated
    except:
        return "error" # signifies that an error occured when adding the user's data in the 'users' table
        
@application.route("/verifyUser", methods = ["POST"])
# route to verify a user's sign in details
def verifyUser():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    data = request.form # assigns the data sent to the API to a variable ('data')

    query = "SELECT EXISTS(SELECT accountID FROM users WHERE email = '%s' AND password = '%s')" % (data['email'], data['password']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = (myCursor.fetchone())[0] # returns the first result of the query result (accountID), if there is a result to be returned
    if result != 0:
        return result # the accountID of the account matching the details inputted by the user is returned 
    else:
        return "none" # the string 'none' is returned if the user's inputted details do not match an account stored in the 'users' MySQL table
    
@application.route("/verifyAccount", methods = ["POST"])
# route to verify that a user's account doesn't already exist
def verifyAccount():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communicationwith mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM users WHERE email = '%s')" % (data['email']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = (myCursor.fetchone())[0] # returns the first result of the query result (accountID), if there is a result to be returned
    if result != 0:
        return "exists" # the string 'exists' is returned if the user's inputted details match an account which already exists in the 'users' MySQL table
    else:
        return "notExists" # the string 'notExists' is returned if the user's inputted details do not match an account which already exists in the 'users' MySQL table
    
@application.route("/view_audioMessages", methods = ["POST"])
# route to determine how many audio messages a particular user has and what the display names are and file details are for these messages
def view_audioMessages():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                       database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communicationwith mydb (MySQL database)
        query = "SELECT messageID, messageName, fileText FROM audioMessages WHERE accountID = '%s'" % (data['accountID']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchall() # returns all the results of the query result (messageName and fileText), if there is a result to be returned
        result_dict = dict() # creates a dictionary to store the results from the executed query
        result_dict["length"] = len(result) # add the key 'length' to the dictionary to store the number of audio messages stored in the 'audioMessages' MySQL table for the concerned user
        for i in result:
            result_dict[str(result.index(i))] = i # adds the name of each audio message and the respective data from the field 'fielText' to the dictionary with keys of an incrementing numerical value
        return jsonify(result_dict) # returns a jsonfied object of the results dictionary using the method 'jsonify'
    except:
        return "error"
    
@application.route("/verify_messageID", methods = ["POST"])
# route to check whether the messageID that has been generated for an audio message does not already exist
def verify_messageID():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM audioMessages WHERE messageID = '%s')" % (data['messageID']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = (myCursor.fetchone()[0]) # returns the first result of the query result (accountID), if there is a result to be returned
    if result != 0:
        return "exists" # the string 'exists' is returned if the messageID generated is already used by another audio message in the 'audioMessages' table
    else:
        return "notExists" # the string 'notExists' is returned if the messageID generated is not already used by another audio message in the 'audioMessages' table
 
@application.route("/verify_messageName", methods = ["POST"])
# route to check whether the message name that the user has inputted has already been assigned to one of their audio messages
def verify_messageName():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query =  "SELECT EXISTS(SELECT * FROM audioMessages WHERE messageName = '%s' AND accountID = '%s')" % (data['messageName'], data['accountID']) # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = (myCursor.fetchone()[0]) # returns the first result of the query result (messageName), if there is a result to be returned
    if result != 0:
        return "exists" # the string 'exists' is returned if the message name is already assigned one of the user's audio messages in the 'audioMessages' table
    else:
        return "notExists" # the string 'notExists' is returned if the message name is not already assigned one of the user's audio messages in the 'audioMessages' table
    
    
@application.route("/update_audioMessages", methods = ["POST"])
# route to add data about a new audio message to the 'audioMessages' table
def update_audioMessages():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                       database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        if data["initialCreation"] == "False":
            query = "UPDATE audioMessages SET messageName = '%s', fileText = '%s' WHERE messageID = '%s'" % (data['messageName'], data['fileText'], data['messageID'])
        else:
            query = "INSERT INTO audioMessages (messageID, messageName, fileText, accountID) VALUES ('%s', '%s', '%s', '%s')" % (data['messageID'], data['messageName'], data['fileText'], data['accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"


@application.route("/update_visitorLog", methods = ["POST"])
# route to add data about a new audio message to the 'audioMessages' table
def update_visitorLog():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                       database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "INSERT INTO visitorLog (visitID, imageTimestamp, faceID, confidence, accountID) VALUES ('%s', '%s', '%s', '%s', '%s')" % (data['visitID'], data['imageTimestamp'], data['faceID'], data['confidence'], data['accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"


@application.route("/view_visitorLog", methods = ["POST"])
def view_visitorLog():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT imageTimestamp, faceID FROM visitorLog WHERE visitID = '%s'" % (data["visitID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()
    return jsonify(result)


@application.route("/update_knownFaces", methods = ["POST"])
# route to add data about a new audio message to the 'audioMessages' table
def update_knownFaces():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    if data['faceName'] == "": # if this is the first time the record with this faceID has been added to the database (from the raspberry pi)
        query = "INSERT INTO knownFaces (faceID, faceName, accountID) VALUES ('%s', '%s', '%s')" % (data['faceID'], data['faceName'], data['accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    else: # called when the user has entered the name for the faceID value and wants to store this value
        query = "UPDATE knownFaces SET faceName = '%s' WHERE faceID = '%s'" % (data['faceName'], data['faceID'])
    myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    mydb.commit() # commits the changes to the MySQL database made by the executed query
    return "success"


@application.route("/view_knownFaces", methods = ["POST"])
def view_knownFaces():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT faceName FROM knownFaces WHERE faceID = '%s'" % (data["faceID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()  # returns the first result of the query result (accountID), if there is a result to be returned
    return jsonify(result)
    
@application.route("/delete_audioMessages", methods = ["POST"])
def delete_audioMessages():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the data sent to the API to a variable ('data')
        mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                       database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "DELETE FROM audioMessages WHERE messageID = '%s'" % (data['messageID'])
        myCursor.execute(query) # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit() # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"
    
    
@application.route("/uploadS3", methods = ["POST"])
# route to upload byte data of the user's personalised audio messages
def uploadS3(): 
    try:
        with open("/etc/keys/S3.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the metadata sent to the API to a variable ('data')
        file = request.files["file"] # assigns the txt file storing the bytes of the audio message to the variable 'file'
        fileName = "/tmp/uploadFile.pkl"
        file.save(fileName) # temporarily saves the txt file in the "/tmp" folder on the AWS server
        s3 = boto3.client("s3", aws_access_key_id=keys["accessKey"], aws_secret_access_key=keys["secretKey"]) # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
        s3.upload_file(Filename=fileName, Bucket=data["bucketName"], Key=data["s3File"]) # uploads the txt file to the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is stored on S3 is the 'messageID' of the audio message which is being stored as a txt file.
        return "success"
    except:
        return "error"
    
@application.route("/downloadS3", methods = ["POST"])
# route to upload byte data of the user's personalised audio messages
def downloadS3():
    try:
        with open("/etc/keys/S3.json", "r") as file:
            keys = json.load(file)
        data = request.form # assigns the metadata sent to the API to a variable ('data')
        if data["bucketName"] == "nea-audio-messages":
            fileName = "/tmp/audioMessage_download.pkl"
        elif data["bucketName"] == "nea-visitor-log":
            fileName = "/tmp/visitorImage_download.png"
        s3 = boto3.client("s3", aws_access_key_id=keys["accessKey"], aws_secret_access_key=keys["secretKey"]) # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
        s3.download_file(Filename=fileName, Bucket=data["bucketName"], Key=data["s3File"])  # downloads the txt file with the name equal to the concerned messageID from the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is downloaded and stored temporarily on the AWS server
        return send_file(fileName, as_attachment = True)
    except:
        return "error"
    
@application.route("/create_ID", methods = ["POST"])
# route to create a unique faceID for the face captured
def create_faceID():
    data = request.form
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    mydb = mysql.connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    while True:  # creates an infinite loop
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits  # creates a concatenated string of all the uppercase and lowercase alphabetic characters and all the digits (0-9)
        ID = (''.join(random.choice(chars) for i in range(43)))+'=' # unique message ID is compatible format for fernet encryption
        if data["field"] == "visitID":
            query = "SELECT EXISTS(SELECT * FROM visitorLog WHERE visitID = '%s')" % (ID)  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        else:
            query = "SELECT EXISTS(SELECT * FROM knownFaces WHERE faceID = '%s')" % (ID)  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchone()[0]  # returns the first result of the query result (accountID), if there is a result to be returned
        if result == 0:
            break
    return ID

@application.route("/get_S3Key", methods = ["POST"])
def get_S3Key():
    data = request.form
    with open("/etc/keys/db.json", "r") as file:
        keys_db = json.load(file)
    with open("/etc/keys/S3.json", "r") as file:
        keys_S3 = json.load(file)
    mydb = mysql.connector.connect(host=(keys_db["host"]), user=(keys_db["user"]), passwd=(keys_db["passwd"]),
                                   database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT * FROM users WHERE accountID = '%s'" % (data["accountID"])
    myCursor.execute(query)
    result = myCursor.fetchone()
    if result != 0:
        key = data["accountID"].encode() # key must be encoded as bytes
        fernet = Fernet(key) # instantiates Fernet encryption key using user's accountID as the encryption key
        accessKey_encoded = fernet.encrypt(keys_S3["accessKey"].encode()) # use Fernet class instance to encrypt the string - string must be encoded to byte string before it is encrypted
        secretKey_encoded = fernet.encrypt(keys_S3["secretKey"].encode()) # use Fernet class instance to encrypt the string - string must be encoded to byte string before it is encrypted
        encodedKeys_dict = {'accessKey_encoded': accessKey_encoded.decode(), 'secretKey_encoded': secretKey_encoded.decode()} # keys must be decoded to be jsonified and sent over API
        return encodedKeys_dict
    else:
        return "error"

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running

