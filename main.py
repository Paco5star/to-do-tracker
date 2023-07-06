from flask import Flask, render_template, redirect, request, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from forms import LoginForm, SignupForm
import secrets 
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os 


secret_key = secrets.token_hex(16)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI1692")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = secret_key
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    tasks = db.relationship('Task',backref='user', lazy=True)
    @staticmethod
    def  is_authenticated():
        return 'user_id' in session
    def authenticate(self,password):
        return self.password == password 


  

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)




todo1 = []
@app.route("/", methods= ['GET', "POST"])
def home():
    if not User.is_authenticated():
        return redirect(url_for('landing'))
    
        
    

    if request.method == "POST":
        todo = request.form.get('todo')
        if todo:
            task = Task(description=todo, user_id=session['user_id'])
            db.session.add(task)
            db.session.commit()
        checked_task_ids = request.form.getlist('checked_tasks')

        # Update the checked status of tasks
        tasks = Task.query.filter_by(user_id=session['user_id']).all()
        for task in tasks:
            if str(task.id) in checked_task_ids:
                task.checked = True
            else:
                task.checked = False

        db.session.commit()

    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    return render_template("index.html", todos = tasks, User=User)

@app.route("/login", methods=["POST","GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', form=form, error='Invalid email or password')
        
    return render_template("login.html", form=form, User = User)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', form=form, error='Email already exists')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form, User=User)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_task/<int:task_id>', methods=["POST"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/landing")
def landing():
    user = User()

    return render_template("landing.html", User = User)

if __name__ == "__main__":
    
    app.run(debug=True)