import flask
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jaslkjakgjalkgjkagjaklgjkd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB.
# with app.app_context():
#     db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    not_exists = True
    if request.method == "POST":
        users = User.query.all()
        for i in users:
            if i.email == request.form['email']:
                not_exists = False
                flash('This email ID already exists')
        if not_exists:
            new_user = User(id=len(User.query.all()) + 1, name=request.form['name'], email=request.form['email'],
                            password=generate_password_hash(request.form['password'],salt_length=8, method="pbkdf2:sha256"))
            db.session.add(new_user)
            db.session.commit()
            if new_user.is_active:
                return render_template('secrets.html', name=new_user.name)

    return render_template("register.html")


@app.route('/login', methods=['GET','POST'])
def login():
    wrong_password = False
    wrong_mail = False
    users = User.query.all()
    if request.method == "POST":
        for i in users:
            if check_password_hash(pwhash=i.password, password=request.form['password']) and i.email == request.form['email']:
                user = User.query.filter_by(email=request.form['email']).first()
                login_user(user)
                return redirect(url_for('secrets',id=user.id))
            elif check_password_hash(pwhash=i.password, password=request.form['password'])==False and i.email == request.form['email']:
                wrong_password = True
            elif i.email != request.form['email'] and check_password_hash(pwhash=i.password, password=request.form['password']):
                wrong_mail = True

        if wrong_password:
            flash('Password is Wrong. Please re-enter the correct password')

        elif wrong_mail:
            flash('That email doesn\'t exist. Please try again')


    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    if User.is_authenticated:
        user = User.query.get(request.args.get('id'))
        return render_template("secrets.html",name=user.name)


@app.route('/logout')
def logout():
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    if current_user.is_authenticated:
        return send_from_directory('static/files', filename='cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
