from flask import Flask, request
from flask_restful import Api

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'application' variable in restful API


@application.route("/") 
# homepage route 
def test():
    return "Working" # if the pipeline and server is working, the text 'Working' is displayed when the homepage is accessed 

@application.route("/users", methods = ["POST", "GET"])
# route to modify the 'users' table
def updateUsers():
    try:
        print(request.method)
    except:
        print(request.method())
    if request.method == "POST":
        try:
            return(request.form["password"])
        except:
            return "Post"
    else:
        return "Not Post"


if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)
    application.run(debug=True)  # begins running the Api server


