from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
import json

with open("config.json", 'r') as c:
    params = json.load(c)["params"]
print(params)
app = Flask(__name__)

# https://myaccount.google.com/u/1/lesssecureapps   Allow less secure app
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['my_gmail'],
    MAIL_PASSWORD=params['my_gmail_pass']
)
mail = Mail(app)

# DATABSE_URI='mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='askarpit')
if params['local_server']:
    DATABASE_URI=params["local_uri"]
else:
    DATABASE_URI = params["prod_uri"]
app.config['SQLALCHEMY_DATABASE_URI'] =DATABASE_URI
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),  nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer,nullable=False)
    message = db.Column(db.String,  nullable=False)
    date = db.Column(db.String)


class Posts(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    content = db.Column(db.String(300), nullable=False)
    date = db.Column(db.String(30), nullable=True)
    image_file= db.Column(db.String(30),  nullable=True)



@app.route('/')
def home():
    posts = Posts.query.filter_by().all()
    return render_template("index.html",posts=posts,params=params)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['POST',"GET"])
def contact():
    if request.method=="POST":
        '''Add to database'''
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        phone = request.form.get('phone')
        print(name, email, phone, message)
        entry = Contact(name=name, email=email, phone=phone, message=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New message from " + name,
                          sender=email,
                          recipients=['201751009@iiitvadodara.ac.in','Kajal123m@gmail.com'],
                          body=message + '\n' + phone)

    return render_template('contact.html')


@app.route('/post/<string:post_slug>', methods=['GET'])
def post(post_slug):
    new_post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=new_post)


@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        print(email==params['admin_email'], password==params['admin_password'])
        if email== params['admin_email'] and password==params['admin_password']:
            print("YEAAAAH")
            return "permission granted"
        else:
            print("LOGIN FAILED")
            return render_template('login.html', params=params)
        # redirect to admin area
    else:
        return render_template('login.html',params=params)


if __name__ == '__main__':
    app.run(debug=True) 