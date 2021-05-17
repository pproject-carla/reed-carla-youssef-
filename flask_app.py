from flask import Flask, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, LoginManager, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# this will be added in bash console (python interpreter)
#from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash



app = Flask(__name__)
app.config["DEBUG"] = True


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
   username="pproject",
   password="orange.668",
   hostname="pproject.mysql.pythonanywhere-services.com",
   databasename="pproject$gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "aisdfhgiauosdhfnalkisdfiluhilasdhf"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = "teacher"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))


  #define a method for this class, used in login route
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

  # define a method for this class, the self.username comes with the class
    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

class Students(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    first_name=db.Column(db.String(256))
    last_name=db.Column(db.String(256))
    email=db.Column(db.String(256))
    major=db.Column(db.String(256))
    fullname=db.column_property(first_name +" "+ last_name)
    assignment = db.relationship('Assignments', cascade="all, delete")

class Assignments(db.Model):
    __tablename__="assignments"
    id = db.Column(db.Integer, primary_key=True)
    assign1 = db.Column(db.String(256))
    assign2 = db.Column(db.String(256))
    assign3 = db.Column(db.String(256))
    assign4 = db.Column(db.String(256))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    student = db.relationship('Students', foreign_keys=student_id)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login.html", error=True)

    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/mainpage/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        results = db.session.query(Assignments).join(Students, Assignments.student).order_by(Students.last_name)
        return render_template("main_page.html", results =results )

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

#Add Student to Student Table#
@app.route('/mainpage/add_student/', methods=["GET", "POST"])
def student_add():
    if request.method == "GET":
        return render_template("student_add.html", students=Students.query.all())

    students = Students(first_name=request.form["first_name"], last_name=request.form["last_name"], email=request.form["email"], major=request.form["major"])
    db.session.add(students)
    db.session.commit()

    return redirect(url_for('student_add'))

@app.route('/mainpage/edit_student/')
def student_edit():
    return render_template("student_edit.html",students=Students.query.all())

#Delete student#
@app.route('/student_delete', methods=["GET", "POST"])
def delete_student():
    if request.method == "GET":
        return render_template("student_edit.html",students=Students.query.all())

    student_delete=Students.query.get(request.form["student_id"])
    db.session.delete(student_delete)
    db.session.commit()

    return render_template("student_edit.html",students=Students.query.all())

#Update Student Information#
@app.route('/mainpage/student_edit', methods=["GET","POST"])
def edit_student():
    if request.method == "GET":
        return render_template("student_edit.html",students=Students.query.all())

    student_edit=Students.query.get(request.form["student_id"])
    firstname_edit = request.form["first_name"]
    lastname_edit = request.form["last_name"]
    email_edit = request.form["email"]
    major_edit = request.form["major"]

    if firstname_edit != '':
        student_edit.first_name=request.form["first_name"]
        db.session.commit()
    if lastname_edit != '':
        student_edit.last_name=request.form["last_name"]
        db.session.commit()
    if email_edit != '':
        student_edit.email=request.form["email"]
        db.session.commit()
    if major_edit != '':
        student_edit.major=request.form["major"]
        db.session.commit()

    return render_template("student_edit.html",students=Students.query.all())

@app.route('/mainpage/grades/', methods=["GET","POST"])
def grade():
    if request.method == "GET":
        grades = db.session.query(Assignments).join(Students, Assignments.student).order_by(Students.last_name)
        return render_template('grades.html', students=Students.query.all(), grades=grades)

    grade=Assignments(assign1=request.form["grade1"], assign2=request.form["grade2"], assign3=request.form["grade3"], assign4=request.form["grade4"], student_id=request.form["s_name"])
    db.session.add(grade)
    db.session.commit()
    return redirect(url_for('grade'))

@app.route('/mainpage/grades/edit', methods=["GET","POST"])
def edit_grade():
    if request.method == "GET":
        grades = db.session.query(Assignments).join(Students, Assignments.student).order_by(Students.last_name)
        return render_template('grades.html', students=Students.query.all(), grades=grades)

    grade_edit=Assignments.query.filter_by(student_id=request.form["s_name"]).first()
    assign1_edit=request.form["grade1"]
    assign2_edit=request.form["grade2"]
    assign3_edit=request.form["grade3"]
    assign4_edit=request.form["grade4"]

    if assign1_edit != '':
        grade_edit.assign1=request.form["grade1"]
        db.session.commit()
    if assign2_edit != '':
        grade_edit.assign2=request.form["grade2"]
        db.session.commit()
    if assign3_edit != '':
        grade_edit.assign3=request.form["grade3"]
        db.session.commit()
    if assign4_edit != '':
        grade_edit.assign4=request.form["grade4"]
        db.session.commit()

    return redirect(url_for('grade'))