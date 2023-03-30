import csv
import datetime
from io import StringIO
from flask import Flask, request, jsonify, session, render_template
import json

# utiliser mysql avec flask
from flask_cors import CORS, cross_origin
import os
import uuid 
from werkzeug.utils import secure_filename
import pyrebase
from flask_session import Session
#import pyrebase
import urllib.request
import pandas as pd
from analyse import analysefunc
# local uploads 
UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENTIONS = {"csv", "png", "jpeg", "gif"}


#filter mime-types 
def allowed_files(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENTIONS

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
#config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config["MYSQL_DB"] = "visualisation"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_COOKIE_SAMESITE'] = "None"
Session(app)

# app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
# session['loggedin'] = False
# session['id'] = ""
# session['email'] = ""
# session['firstname'] = ""
# session['lastname'] = ""
# session['password'] = ""
# mysql = MySQL(app)
cors = CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

#fire base config
config = {
    "apiKey": "AIzaSyBAghCslXj0tiegqo-_BJzOeaLZH_DvpSY",
  "authDomain": "visualisation-c78b5.firebaseapp.com",
  "projectId": "visualisation-c78b5",
  "storageBucket": "visualisation-c78b5.appspot.com",
  "messagingSenderId": "584789840609",
  "appId": "1:584789840609:web:04e2cabef94a4a8c365da0",
  "serviceAccount": "./keyfile.json",
  "databaseURL": "https://visualisation-c78b5-default-rtdb.firebaseio.com"

}

#init firebase app
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
#real time database instance
db = firebase.database()
#storage
storage = firebase.storage()
@app.route('/')
def index():
    return render_template('index.html')

# @app.route("/api/posts", methods=["GET"])
# def index():
#     if request.method == "GET":
#         return jsonify(data="posts main response")

# @app.route("/api/addposts", methods=["POST"])
#     if request.method == "POST":
        
@app.route("/api/register", methods=["POST"])
def register():
    if request.method == "POST":

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            # email = "ahfmeereizi@gmail.com"
            # password = "11111tbrtbrtb"
        # Where I added my shit
        #create the user
            user = auth.create_user_with_email_and_password(email, password)
            # #login the user right away
            # user = auth.sign_in_with_email_and_password(email, password)   
            userinfo = {
                "email":email,
                "password":password,
                "firstname":firstname,
                "lastname":lastname
            }
            local = auth.get_account_info(user['idToken'])
            localId = local['users'][0]['localId']
           
            # # Wher I ended my shit
            # # json_data = request.get_json()
            # # print(json_data)
            # # firstname = json_data['firstname']
            # # lastname = json_data['lastname']
            # # email=json_data['email']
            # # password=json_data['password']

            # # Save user data in Firebase Realtime Database
            db.child('users').child(localId).set(userinfo)
            status = "success"
        except:
            status = "email already exists"
            #get cursor to exec the mysql functions
        # try:
        #     cur = mysql.connection.cursor()
        #     cur.execute(""" INSERT INTO user (firstname, lastname, email, password) VALUES (%s, %s, %s, %s)  """,
        #         (firstname, lastname, email, password)
        #     )
        #     mysql.connection.commit()
        #     cur.close()
        #     status = "success"
        # except: 
        #     status = 'this user is already registered'
    return jsonify({'result': status})


@app.route('/api/login', methods=['POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access

        # json_data = request.get_json()
        # print(json_data)
        # firstname = json_data['firstname']
        # lastname = json_data['lastname']
        # email=json_data['email']
        # password=json_data['password']
        email = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        try:
        # Verify user credentials with Firebase Authentication
            # email = "ahfmeereizi@gmail.com"
            # password = "11111tbrtbrtb"
            user = auth.sign_in_with_email_and_password(email, password)
            print("AAA")
            local = auth.get_account_info(user['idToken'])
            localId = local['users'][0]['localId']
            print(localId)
            orderedDict = db.child("users").order_by_key().equal_to(localId).limit_to_first(1).get()
            items = list(orderedDict.val().items())
            print(items[0][1]['email'])
            # user_data = users_ref.child(localId).get()
            # print(user_data)
            # session['user'] = user.uid
            session['loggedin'] = True
            session['id'] = items[0][0]
            session['email'] = items[0][1]['email']
            session['firstname'] = items[0][1]['firstname']
            session['lastname'] = items[0][1]['lastname']
            status = "success"
            return jsonify({'status': True})
        except:
            print("error")
            status = "shit"
            return jsonify({'status': False})

        # cursor = mysql.connection.cursor()
        # cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        # # Fetch one record and return result
        # account = cursor.fetchone()
        # print(type(account))
        # print(account)
        # # If account exists in accounts table in out database
        # if account:
        #     # Create session data, we can access this data in other routes
        #     session['loggedin'] = True
        #     session['id'] = account[0]
        #     session['email'] = account[3]
        #     session['firstname'] = account[1]
        #     session['lastname'] = account[2]
        #     session['password'] = account[4]
        #     print(session)
        #     return jsonify({'status': True})
        # else:
        #     # Account doesnt exist or username/password incorrect
        #     msg = 'Incorrect email/password!'
        #     return jsonify({'status': False})
        
@app.route('/api/getuser',  methods=['POST'])
def getuser():
    if request.method == "POST":
        print(session)
        if session.get("loggedin"):
            # return jsonify({'status': "heeof"})
            return jsonify({"id": session['id'], "email": session["email"], "firstname": session['firstname'], "lastname": session['lastname']})
        else:
            return None

@app.route('/api/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)

   return jsonify({'status': "logged out"})


@app.route("/api/addpost", methods=["POST"])
def addpost():
    if request.method == "POST":
        # print(request.form, flush=True)

        # title = request.form.get("title")
        # content = request.form.get("content")
        cover = request.files["cover"]
        if cover.filename.split(".")[1] == "csv":
            filename = str(uuid.uuid4())
            filename += "."
            filename += cover.filename.split(".")[1]

            #save the file inside the uploads folder
            cover.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            #local file
            local_filename = "./uploads/"
            local_filename += filename   

            #firebase filename
            firebase_filename = "uploads/"
            firebase_filename += filename

            #upload the file
            storage.child(firebase_filename).put(local_filename)
            #get the url of the file
            cover_image = storage.child(firebase_filename).get_url(None)
            infofile = {
                "filename": filename,
                "URL": cover_image
            }
            print("le fichier ajouté", filename, cover_image)
            #get cursor to exec the mysql functions

            print(session['firstname'])
            try:
                
                localId = session["id"]
                db.child("users").child(localId).child("csvfile").push(infofile)
                print("gggggggggggggggggggggggggggggggg")
                # orderedDict = db.child("users").order_by_key().equal_to(localId).limit_to_first(1).get()

            # cur = mysql.connection.cursor()
            # cur.execute(""" INSERT INTO fichier ( cover, covername) VALUES (%s, %s)  """, (cover_image, filename))
            # mysql.connection.commit()
            # cur.close()
                status = filename

                
                
            except: 
                print("ffffffffffffffffffffff")
                status = 'fail'
                

            # os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            return jsonify({"data" : status})
        else:

            return jsonify({"data" : "fail"})

@app.route('/api/protected',  methods=['GET'])
def protected():
    if 'loggedin' in session:
        if session['loggedin']:
            return jsonify({"authenticated" : True})
        else:
            return jsonify({"authenticated" : False})
    else:
        return jsonify({"authenticated" : False})




@app.route("/api/analyse", methods=["POST"])   
def analyse():
    if request.method == "POST":
        print(request.form)
        data1 = request.get_json()
        filename = data1.get('filename')
        filename = 'uploads/' + filename
        print(filename)
        print(type(filename))
        blob = storage.bucket.blob(filename)
        url = blob.generate_signed_url(
            expiration=datetime.timedelta(minutes=15),
            method="GET"
        )

        if filename.split(".")[1] == "csv":
        # Retrieve contents of uploaded file from Firebase Storage
            with urllib.request.urlopen(url) as url:
                content = url.read().decode("latin1")

            # csv_data = pd.read_csv(StringIO(content))

        # Do something with CSV data...
        # For example, print out the first 5 rows of the CSV file
            # print(csv_data.head())
            print('avant')
            result = analysefunc(content)
            print('apres')
            #local filename
            filenamejson = filename.split(".")[0]
            filenamejson += ".json"


            #firebase filename
            firebase_filename = filenamejson
            with open(filenamejson, "w") as f:
                jsonify(json.dump(result, f))

            storage.child(firebase_filename).put(filenamejson)
            print("fichier enregistré")
            #get the url of the file
            cover_image = storage.child(firebase_filename).get_url(None)
           
            infofile = {
                "filename": filenamejson,
                "URL": cover_image
            }
            try:
                if "id" in session:
                    localId = session["id"]
                    db.child("users").child(localId).child('jsonfiles').push(infofile)
                    
                # cur = mysql.connection.cursor()
                # cur.execute(""" INSERT INTO fichier ( cover, covername) VALUES (%s, %s)  """, (cover_image, filename))
                # mysql.connection.commit()
                # cur.close()
                status = filenamejson
            except: 
                status = 'success'
        else:
            status = "nothing"
        return jsonify({"json" : status})
    else:
        return {{"json" : "nothing"}}
    


#recuper fichier
#analyser
#stocker resultat dans un fichier json
#envoyer fichier json au front


   # Redirect to login page
if __name__== "__main__":
    app.run()


