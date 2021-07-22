from flask import Flask, request
from flask_restful import Api

app = Flask(__name__) # the file is wrapped in the Flask constructer which enables the file to be a web-application
api = Api(app)  # wrap 'app' variable in restful Api

@app.route("/")
def test():
    return "Working"

if __name__ == "__main__":  # if the name of the file is the main program (not a module imported from another file)
    app.run(debug=True)  # begins running the Api server


