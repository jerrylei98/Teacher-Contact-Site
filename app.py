from flask import Flask, render_template, session, request, redirect
import database
import json

app = Flask(__name__)

@app.route("/")
def index():
    with open('../secret_key/gmail.json') as data_file:
        data = json.load(data_file)
    client_id = data['web']['client_id']
    return render_template("index.html", username = session.get('username'), auth = session.get('auth'), client_id = client_id)

@app.route('/addUser')
def addUser():
    session['username'] = username = request.args.get('username', 0, type=str)
    session['email'] = email = request.args.get('email', 0, type=str)
    session['auth'] = auth = request.args.get('auth', 0, type=str)
    return redirect("/")

@app.route("/testLogin", methods=["GET", "POST"])
def testLogin():
    if request.method == "GET":
        if session.get('username') != None:
            return redirect("/")
        else:
            return render_template("login.html", username = None, auth = None)
    else:
        username = request.form.get("login")
        session['username'] = username
        session['auth'] = 'test'
        return redirect("/")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/classes")
@app.route("/classes/<CLASSCODE>")
def classes():
    return redirect("/")

@app.route("/createClass", methods=["GET", "POST"])
def createClass():
    if request.method == "GET":
        if session.get('username') == None or session.get('auth') != 'teacher':
            return redirect("/")
        else:
            return render_template("createClass.html", username = session.get('username'), auth = session.get('auth'), email = session.get('email'))
    else:
        pass

@app.route("/contactInfo", methods=["GET", "POST"])
def contactInfo():
    if request.method == "GET":
        if session.get('username') == None or session.get('auth') != 'student':
            return redirect("/")
        else:
            return render_template("contactInfo.html", username = session.get('username'), auth = session.get('auth'), email = session.get('email'))
    else:
        pass

@app.route("/addClasses", methods=["GET", "POST"])
def addClasses():
    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "supersecretkey"
    app.run(host = '0.0.0.0', port = 8000)
