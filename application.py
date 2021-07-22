from flask import Flask, request
from flask_restful import Api

application = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(application)  # wrap 'app' variable in restful Api


@application.route("/")
def test():
    return "Working"

@application.route("/users")
def updateUsers():
    return "Hello"
    #if request.method == "POST":
        #return(request.form["password"])


if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)
    application.run(debug=True)  # begins running the Api server


