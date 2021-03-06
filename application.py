from flask import Flask, request, jsonify, send_file
from mysql import connector
import boto3
import json
import random
import string
from cryptography.fernet import Fernet
import time

application = Flask(
    __name__)  # wraps file using the Flask constructor and stores it as the central object called 'application'


@application.route("/")
# homepage route 
def test():
    return "Working"  # if the pipeline and server is working, the text 'Working' is displayed when the homepage route is accessed


@application.route("/updateUsers", methods=["POST"])
# route to add a new user to the 'users' table
def updateUsers():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                 database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "INSERT INTO users(accountID, firstName, surname, email, password) VALUES ('%s','%s','%s','%s','%s')" % (
        data['accountID'], data['firstName'], data['surname'], data['email'], data[
            'password'])  # MySQL query to add the data sent with the API to the appropriate columns in the 'users' table
        myCursor.execute(query)  # executes the query in the MySQL database
        mydb.commit()  # commits the changes to the MySQL database made by the executed query
        return "success"  # confirms that MySQL database was successfully updated
    except:
        return "error"  # signifies that an error ocurred when adding the user's data in the 'users' table


@application.route("/verifyUser", methods=["POST"])
# route to verify a user's sign in details
def verifyUser():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    query = "SELECT EXISTS (SELECT * FROM users WHERE email = '%s' AND password = '%s')" % (data['email'], data[
        'password'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = (myCursor.fetchone())[
        0]  # returns the first result of the query result (accountID), if there is a result to be returned
    if result == 1:
        query = "SELECT accountID FROM users WHERE email = '%s' AND password = '%s'" % (data['email'], data[
            'password'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = (myCursor.fetchone())  # returns the first result of the query result (accountID), if there is a result to be returned
        return {'result': result[0]}
    else:
        return {'result': 'none'}


@application.route("/verifyAccount", methods=["POST"])
# route to verify that a user's account doesn't already exist
def verifyAccount():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM users WHERE email = '%s')" % (data[
        'email'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[0]  # returns 1 if there is a result and 0 if not
    if result == 1:
        return "exists"  # the string 'exists' is returned if the user's inputted details match an account which already exists in the 'users' MySQL table
    else:
        return "notExists"  # the string 'notExists' is returned if the user's inputted details do not match an account which already exists in the 'users' MySQL table


@application.route("/view_audioMessages", methods=["POST"])
# route to determine how many audio messages a particular user has and what the display names are and file details are for these messages
def view_audioMessages():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM audioMessages WHERE accountID = '%s')" % (data[
        'accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[0] # returns '1' if records exist with user's account ID (i.e. if the user has created audio messages) and '0' if not
    if result == 1:
        query = "SELECT messageID, messageName, messageText FROM audioMessages WHERE accountID = '%s'" % (data['accountID'])
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchall()  # returns all the results of the query  
        result_dict = dict()  # creates a dictionary to store the results from the executed query
        result_dict["length"] = len(
            result)  # add the key 'length' to the dictionary to store the number of audio messages stored in the 'audioMessages' MySQL table for the concerned user
        for i in result:
            result_dict[str(result.index(i))] = i  # adds the name of each audio message and the respective data from the field 'fielText' to the dictionary with keys of an incrementing numerical value
        return {'result': result_dict}  # returns a jsonfied object of the results dictionary using the method 'jsonify'
    else:
        return {'result': 'none'}


@application.route("/verify_messageID", methods=["POST"])
# route to check whether the messageID that has been generated for an audio message does not already exist
def verify_messageID():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM audioMessages WHERE messageID = '%s')" % (data[
        'messageID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[
        0]  # returns all the results of the query result (messageName and messageText), if there is a result to be returned
    if result == 1:
        return "exists"  # the string 'exists' is returned if the messageID generated is already used by another audio message in the 'audioMessages' table
    else:
        return "notExists"  # the string 'notExists' is returned if the messageID generated is not already used by another audio message in the 'audioMessages' table


@application.route("/verify_messageName", methods=["POST"])
# route to check whether the message name that the user has inputted has already been assigned to one of their audio messages
def verify_messageName():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM audioMessages WHERE messageName = '%s' AND accountID = '%s')" % (
    data['messageName'], data[
        'accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[
        0]  # returns all the results of the query result (messageName and messageText), if there is a result to be returned
    if result == 1:
        return "exists"  # the string 'exists' is returned if the message name is already assigned one of the user's audio messages in the 'audioMessages' table
    else:
        return "notExists"  # the string 'notExists' is returned if the message name is not already assigned one of the user's audio messages in the 'audioMessages' table


@application.route("/update_audioMessages", methods=["POST"])
# route to add data about a new audio message to the 'audioMessages' table
def update_audioMessages():
    try:
        with open("/etc/keys/db.json", "r") as file:  # load file storing credentials to access RDS database
            keys = json.load(file)  # convert the json file into a json object
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                 database="ebdb")  # initialise connection to database
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with 'mydb' (MySQL database session)
        if data['initialCreation'] == "False":  # if audio message already exists in database
            query = "UPDATE audioMessages SET messageName = '%s', messageText = '%s' WHERE messageID = '%s'" % (
            data['messageName'], data['messageText'],
            data['messageID'])  # update message name and message text (if appropriate)
        else:  # if audio message is to be added to database for the first time
            query = "INSERT INTO audioMessages (messageID, messageName, messageText, accountID) VALUES ('%s', '%s', '%s', '%s')" % (
            data['messageID'], data['messageName'], data['messageText'], data['accountID'])
            # data for new audio message is inserted into the table 'audioMessages'
        myCursor.execute(query)  # the query is executed in the MySQL database
        mydb.commit()  # commits the changes to the MySQL database made by the executed query
        return "success"  # 'success' returned if changes are made successfully
    except:
        return "error"  # 'error' returned if there is an error in the process


@application.route("/update_visitorLog", methods=["POST"])
# route to add data about a new visit to the 'visitorLog' table
def update_visitorLog():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                 database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "INSERT INTO visitorLog (visitID, imageTimestamp, faceID, accountID) VALUES ('%s', '%s', '%s', '%s')" % (
        data['visitID'], data['imageTimestamp'], data['faceID'], data[
            'accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit()  # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"


@application.route("/view_visitorLog", methods=["POST"])
# retrieve details for a particular visit from the table 'visitorLog'
def view_visitorLog():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT imageTimestamp, faceID FROM visitorLog WHERE visitID = '%s'" % (data["visitID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()
    return jsonify(result)


@application.route("/get_visitorLog", methods=["POST"])
# route to retrieve data about the visits associated with a user's account from the 'visitorLog' table
def get_visitorLog():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT imageTimestamp, faceID, visitID FROM visitorLog WHERE accountID = '%s'" % (data["accountID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchall()
    return jsonify(result)


@application.route("/get_faceName", methods=["POST"])
# retrieve the name of a visitor given their face ID from the table 'knownFaces'
def get_faceName():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query =  "SELECT faceName FROM knownFaces WHERE faceID = '%s'" % (data["faceID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()
    return jsonify(result)


@application.route("/get_averageTime", methods=["POST"])
# find the average time of day when the user's doorbell is rung
def get_averageTime():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT AVG(SUBSTRING(imageTimestamp,1,5)) FROM visitorLog WHERE accountID = '%s'" % (data["accountID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[0]
    return {'result': result}


@application.route("/get_averageRate", methods=["POST"])
# find the average number of visits per day to the user's doorbell
def get_averageRate():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT COUNT(*) FROM visitorLog WHERE accountID = '%s'" % (data["accountID"]) # retrieve total number of visits for a user's account
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    count = myCursor.fetchone()[0] # total number of visits to user's dooorbell
    query = "SELECT MIN(SUBSTRING(imageTimestamp, 7)) FROM visitorLog WHERE accountID = '%s'" % (data["accountID"]) # retrieve time of first recorded visit to user's doorbell
    myCursor.execute(query)
    initialTime = myCursor.fetchone()[0] # time when user's doorbell first rung
    currentTime = time.time()
    totalDays = (currentTime-float(initialTime))/24/3600 # total days passed since first visit to user's doorbell
    averageRate = count/totalDays # average number of visits to user's doorbell
    return {'result': averageRate}


@application.route("/latest_visitorLog", methods=["POST"])
# retrieve the details about the latest visit the user's doorbell
def latest_visitorLog():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT visitID, faceID FROM visitorLog WHERE accountID = '%s' ORDER BY imageTimestamp DESC)" % (
    data["accountID"])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[
        0]  # returns all the results of the query result (messageName and messageText), if there is a result to be returned
    if result == 1:
        query = "SELECT visitID, faceID FROM visitorLog WHERE accountID = '%s' ORDER BY imageTimestamp DESC" % (
        data["accountID"])
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchone()
        return {'result': result}
    else:
        return {'result': 'none'}


@application.route("/update_knownFaces", methods=["POST"])
# route to add data about a new audio message to the 'knownFaces' table
def update_knownFaces():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    if data[
        'faceName'] == "":  # if this is the first time the record with this faceID has been added to the database (from the raspberry pi)
        query = "INSERT INTO knownFaces (faceID, faceName, accountID) VALUES ('%s', '%s', '%s')" % (
        data['faceID'], data['faceName'], data[
            'accountID'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
    else:  # called when the user has entered the name for the faceID value and wants to store this value
        query = "UPDATE knownFaces SET faceName = '%s' WHERE faceID = '%s'" % (data['faceName'], data['faceID'])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    mydb.commit()  # commits the changes to the MySQL database made by the executed query
    return "success"



@application.route("/delete_audioMessages", methods=["POST"])
# delete audio message record from 'audioMessage' table
def delete_audioMessages():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                 database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        query = "DELETE FROM audioMessages WHERE messageID = '%s'" % (data['messageID'])
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit()  # commits the changes to the MySQL database made by the executed query
        return "success"
    except:
        return "error"


@application.route("/uploadS3", methods=["POST"])
# route to upload byte data of the user's personalised audio messages
def uploadS3():
    try:
        with open("/etc/keys/S3.json", "r") as file:
            keys = json.load(file)
        data = request.form  # assigns the metadata sent to the API to a variable ('data')
        file = request.files[
            "file"]  # assigns the txt file storing the bytes of the audio message to the variable 'file'
        fileName = "/tmp/uploadFile.pkl"
        file.save(fileName)  # temporarily saves the txt file in the "/tmp" folder on the AWS server
        s3 = boto3.client("s3", aws_access_key_id=keys["accessKey"], aws_secret_access_key=keys[
            "secretKey"])  # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey' sent to the API
        s3.upload_file(Filename=fileName, Bucket=data["bucketName"], Key=data[
            "s3File"])  # uploads the txt file to the S3 bucket called 'nea-audio-messages'. The name of the txt file when it is stored on S3 is the 'messageID' of the audio message which is being stored as a txt file.
        return "success"
    except:
        return "error"


@application.route("/downloadS3", methods=["POST"])
# route to download pickled byte data of the user's personalised audio messages or image file of visitor from AWS S3 storage
def downloadS3():
    try:
        with open("/etc/keys/S3.json", "r") as file:  # load file storing pair of keys required to establish connection with S3 storage server
            keys = json.load(file)  # convert the json file into a json object
        data = request.form  # assigns the metadata sent to the API to a variable ('data')
        if data["bucketName"] == "nea-audio-messages":
            fileName = "/tmp/audioMessage_download.pkl"  # file location in eb environment
        elif data["bucketName"] == "nea-visitor-log":
            fileName = "/tmp/visitorImage_download.png"  # file location in eb environment
        s3 = boto3.client("s3", aws_access_key_id=keys["accessKey"], aws_secret_access_key=keys["secretKey"])
        # initialises a connection to the S3 client on AWS using the 'accessKey' and 'secretKey'
        s3.download_file(Filename=fileName, Bucket=data["bucketName"], Key=data["s3File"])
        # downloads file name equal 's3file' from the S3 bucket with name 'bucketName' and stores this file in the '/tmp' directory of the eb environment
        return send_file(fileName, as_attachment=True) # returns the downloaded file to the client
    except:
        return "error" # 'error' returned if there is an error in the process


@application.route("/create_ID", methods=["POST"])
# route to create a unique ID (face ID, visit ID or account ID)
def create_ID():
    data = request.form
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    while True:  # creates an infinite loop
        chars = string.ascii_uppercase + string.ascii_lowercase + string.digits  # creates a concatenated string of all the uppercase and lowercase alphabetic characters and all the digits (0-9)
        ID = (''.join(random.choice(chars) for i in
                      range(43))) + '='  # unique message ID is compatible format for fernet encryption
        if data["field"] == "visitID":
            query = "SELECT EXISTS(SELECT * FROM visitorLog WHERE visitID = '%s')" % (
                ID)  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        elif data["field"] == "accountID":
            query = "SELECT EXISTS(SELECT * FROM users WHERE accountID = '%s')" % (
                ID)  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        elif data["field"] == "faceID":
            query = "SELECT EXISTS(SELECT * FROM knownFaces WHERE faceID = '%s')" % (
                ID)  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchone()[
            0]  # returns the first result of the query result (accountID), if there is a result to be returned
        if result == 0:
            break
    return ID


@application.route("/get_S3Key", methods=["POST"])
# route to retrieve the pair of keys required to interact with AWS S3 storage server
def get_S3Key():
    try:
        with open("/etc/keys/db.json", "r") as file:  # load file storing credentials to access RDS database
            keys = json.load(file)  # convert the json file into a json object
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]), database="ebdb")  # initialise connection to database
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with 'mydb' (MySQL database session)
        with open("/etc/keys/S3.json", "r") as file:  # load file storing pair of keys required to establish connection with S3 storage server
            keys_S3 = json.load(file)  # convert the json file into a json object
        query = "SELECT * FROM users WHERE accountID = '%s'" % (data["accountID"])
        myCursor.execute(query)
        result = myCursor.fetchone() # retrieve first matching record from MySQL database
        if result != 0: # verifies if an account exists with the specified accountID
            key = data["accountID"].encode()  # key must be encoded as bytes
            fernet = Fernet(key)  # instantiates Fernet encryption object using user's accountID as the encryption key
            accessKey_encrypted = fernet.encrypt(keys_S3["accessKey"].encode())  # use Fernet class instance to encrypt the string - string must be encoded to byte string before it is encrypted
            secretKey_encrypted= fernet.encrypt(keys_S3["secretKey"].encode())  # use Fernet class instance to encrypt the string - string must be encoded to byte string before it is encrypted
            encryptedKeys_dict = {'accessKey_encrypted': accessKey_encrypted.decode(),
                                  'secretKey_encrypted': secretKey_encrypted.decode()}  # keys must be decoded to be jsonified and returned by API
            return encryptedKeys_dict
        else:
            return "error"
    except:
        return "error"

@application.route("/update_SmartBellIDs", methods=["POST"])
# route to udpate details about SmartBell pairings in table 'SmartBellIDs'
def update_SmartBellIDs():
    try:
        with open("/etc/keys/db.json", "r") as file:
            keys = json.load(file)
        data = request.form  # assigns the data sent to the API to a variable ('data')
        mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                                 database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
        myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
        if 'accountID' not in data:  # if request is to add a new id, not a new accountID
            query = "INSERT INTO SmartBellIDs (id) VALUES ('%s')" % (data[
                'id'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        else:
            query = "UPDATE SmartBellIDs SET accountID = ('%s') WHERE id = '%s'" % (data['accountID'], data[
                'id'])  # 'query' variable stores string with MySQL command that is to be executed. The '%s' operator is used to insert variable values into the string.
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        mydb.commit()  # commits the changes to the MySQL database made by the executed query
        return 'True'
    except:
        return 'False'


@application.route("/verifyPairing", methods=["POST"])
# route to check whether user has successfully paired with the a particular SmartBell
def verifyPairing():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT accountID FROM SmartBellIDs WHERE id = ('%s')" % (data['id'])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()  # returns the first result of the query result (accountID), if there is a result to be returned
    return {'result': result[0]}


@application.route("/checkPairing", methods=["POST"])
# route to check whether a particular SmartBell ID already exists
def checkPairing():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM SmartBellIDs WHERE id = ('%s'))" % (data['id'])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[
        0]  # returns the first result of the query result (accountID), if there is a result to be returned
    if result == 1:
        return 'exists'
    else:
        return 'notExists'


@application.route("/getPairing", methods=["POST"])
# route to retrieve the pairing status for a particular user account
def getPairing():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT EXISTS(SELECT * FROM SmartBellIDs WHERE accountID = ('%s'))" % (data['accountID'])
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchone()[
        0]  # returns the first result of the query result (accountID), if there is a result to be returned
    if result == 1:
        query = "SELECT id FROM SmartBellIDs WHERE accountID = ('%s')" % (data['accountID'])
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchone()
        return {'result': result[0]}
    else:
        return {'result': 'none'}


@application.route("/checkFaces", methods=["POST"])
# route to check whether the duplicate face names exist for the same user's account
def checkFaces():
    with open("/etc/keys/db.json", "r") as file:
        keys = json.load(file)
    data = request.form  # assigns the data sent to the API to a variable ('data')
    mydb = connector.connect(host=(keys["host"]), user=(keys["user"]), passwd=(keys["passwd"]),
                             database="ebdb")  # initialises the database using the details sent to API, which can be accessed with the 'request.form()' method
    myCursor = mydb.cursor()  # initialises a cursor which allows communication with mydb (MySQL database)
    query = "SELECT faceName FROM knownFaces WHERE accountID = '%s' GROUP BY faceName HAVING COUNT(faceName) > 1" % (
    data['accountID']) # select all face names which appear in more than one record in 'knownFaces' for the same user account
    myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    result = myCursor.fetchall()
    faceIDs = []
    for faceName in result: # iterate through duplicate face names
        query = "SELECT faceID FROM knownFaces WHERE faceName = '%s' AND accountID = '%s' " % (
        faceName[0], data['accountID']) # get the face ID for each duplicate face name
        myCursor.execute(
            query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
        result = myCursor.fetchall()
        faceIDs.append(result)
        faceIDs_delete = result[1:] # get the face IDs of duplicate names which are to be deleted from database
        faceID_keep = result[0][0] # get the base face ID which is to remain stored in database
        for faceID in faceIDs_delete:
            query = "DELETE FROM knownFaces WHERE faceID = '%s' AND accountID = '%s'" % (faceID[0], data['accountID']) # delete face IDs of duplicate names 
            myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
            query = "UPDATE visitorLog SET faceID = '%s' WHERE faceID = '%s' AND accountID = '%s'" % (
            faceID_keep, faceID[0], data['accountID']) # update visitor log to store same face ID for all visits where visitor has same name
            myCursor.execute(query)  # the query is executed in the MySQL database which the variable 'myCursor' is connected to
    mydb.commit()  # commits the changes to the MySQL database made by the executed query
    response = jsonify(faceIDs)
    return response


if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)...
    application.run(debug=True)  # ...then the API server begins running
