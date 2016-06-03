from flask import Flask, render_template, session, request, redirect, jsonify
import database
import utils
import json

app = Flask(__name__)

with open('../secret_key/gmail.json') as data_file:
    data = json.load(data_file)
client_id = data['web']['client_id']

@app.route("/")
def index():
    return render_template("index.html", client_id = client_id, username = session.get('username'), auth = session.get('auth'))

@app.route('/addUser')
def addUser():
    if request.is_xhr:
        session['username'] = request.args.get('username', 0, type=str)
        session['email'] = request.args.get('email', 0, type=str)
        session['auth'] = request.args.get('auth', 0, type=str)
        if session.get('auth') == 'teacher':
            database.create_teacher(session.get('username'), session.get('email'))
        else:
            database.create_student(session.get('username'), session.get('email'))
        return jsonify()
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/myClasses")
def myClasses():
    if session.get('auth') != 'student':
        return redirect("/")
    else:
        return render_template("classes.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), classes = database.find_student_classes(session.get('email')))

@app.route("/classes")
@app.route("/classes/<class_id>", methods=["GET", "POST"])
def classes(class_id = ""):
    if len(class_id) < 1:
        if session.get('auth') != 'teacher':
            return redirect("/")
        else:
            return render_template("classes.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), classes = database.find_teacher_classes(session.get('email')))
    else:
        c1 = database.find_class(class_id)
        if c1 == None:
            return redirect("/")
        if request.method == "GET":
            return render_template("class.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), class_one = c1, students = database.all_students_in_class(class_id))
        if request.method == "POST":
            button = request.form['button']
            if button == "Enroll in Class":
                database.add_to_class(session.get('email'), class_id)
                return redirect("/classes/"+class_id)
            if button == "Leave Class":
                database.remove_from_class(session.get('email'), class_id)
                return redirect("/classes/"+class_id)
            if button == "Email Multiple Students":
                return redirect("/sendMail/"+class_id)
            if button == "Confirm Delete":
                database.delete_class(class_id)
                return redirect("/classes")

@app.route("/sendMail/<class_id>", methods=["GET","POST"])
def sendMail(class_id):
    c1 = database.find_class(class_id)
    if c1 == None:
        return redirect("/")
    if request.method == "GET":
        return render_template("sendMail.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), class_one = c1, students = database.all_students_in_class(class_id))
    if request.method == "POST":
        button = request.form['button']
        checkbox = request.form['checkbox']
        #database.log_mail (FUNCTION THAT CLIENT ASKED FOR)
        if button == "Go to Email Page":
            to = request.form.getlist("checks")
            body = request.form.get("body_name")
            subject = request.form.get("subject_name")
            template = ""
            teacher_name = session.get('username')
            if checkbox == "late_email":
                template = "late_email"
            if checkbox == "":
                template == ''
            gmail_link = utils.make_link(body, to, subject, template,teacher_name)
            for student in request.form.getlist("checks"):
                database.add_log(session.get('username'),student)
            return redirect(gmail_link)

@app.route("/createClass", methods=["GET", "POST"])
def createClass():
    if request.method == "GET":
        if session.get('auth') != 'teacher':
            return redirect("/")
        else:
            return render_template("createClass.html",client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'))
    else:
        database.create_class(session.get('username'), session.get('email'), request.form.get('course_code'), request.form.get('course_name'), request.form.get('course_period'))
        return redirect("/")

def student(student_id = ""):
    if session.get('auth') != 'teacher':
        return redirect("/")
    elif database.check_contact_info(student_id) == None:
        return redirect("/")
    return render_template("contactInfo.html", client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'), student = database.check_contact_info(student_id))

@app.route("/contactInfo", methods=["GET", "POST"])
@app.route("/contactInfo/<student_id>", methods=["GET", "POST"])
def contactInfo(student_id=""):
    if request.method == "GET":
        if session.get('auth') == 'student':
            if len(student_id) > 0:
                return redirect("/contactInfo")
            else:
                return render_template("contactInfo.html", client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'), student = database.check_contact_info(session.get('email')))
        elif session.get('auth') == 'teacher':
            if database.check_contact_info(student_id) == None:
                return redirect("/")
            else:
                return render_template("contactInfo.html", client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'), student = database.check_contact_info(student_id))
        else:
            return redirect("/")
    else:
        database.add_contact_info(session.get('email'), request.form.get('sname'), request.form.get('sphone'), request.form.get('address'), request.form.get('pname'), request.form.get('pphone'), request.form.get('pemail'), request.form.get('gname'), request.form.get('gphone'), request.form.get('gemail'))
        return redirect("/")

@app.route("/addClasses", methods=["GET", "POST"])
def addClasses():
    if request.method == "GET":
        if session.get('auth') != 'student':
            return redirect("/")
        else:
            return render_template("addClass.html",client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'))
    else:
        button = request.form['button']
        if button == "Look":
            checked = request.form.getlist("checks")
            return render_template("addClass.html",client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'), classes = database.all_classes_in_period(checked))
        else:
            return render_template("addClass.html",client_id = client_id, username = session.get('username'), auth = session.get('auth'), email = session.get('email'))#,database.all_classes_in_period())
    return redirect("/")

@app.route("/log", methods=["GET","POST"])
@app.route("/log/<student_name>/<time>", methods=["GET","POST"])
def log(student_name = "", time = ""):
    if request.method == "GET":
        if time == "":
            if session.get('auth') != 'teacher':
                return redirect("/")
            else:
                return render_template("log.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), logs = database.find_log(session.get('username')))
        else:
            return render_template("logInfo.html",student_name=student_name,time=time)
            #database.delete_log(session.get('username'),student_name,time)
            #return render_template("log.html",client_id = client_id, username = session.get('username'), auth=session.get('auth'), logs = database.find_log(session.get('username')))

@app.route("/logInfo")
def logInfo():
    return "test"

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "supersecretkey"
    app.run(host = '0.0.0.0', port = 8000)
