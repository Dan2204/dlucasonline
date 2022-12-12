import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = "Don'ttrythisathomefolks!@!@!£$"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(20), unique=True, nullable=False)
  password_hash = db.Column(db.String(128))

  def set_password(self, password: str):
    self.password_hash = generate_password_hash(password)
  
  def check_password(self, password: str):
    return check_password_hash(self.password_hash, password)


class Project(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  project_type = db.Column(db.String(150), nullable=False)
  title = db.Column(db.String(150), nullable=False)
  sub_title = db.Column(db.String(150), nullable=False)
  project_general = db.Column(db.String(250), nullable=False)
  project_tools = db.Column(db.String(250), nullable=False)
  project_languages = db.Column(db.String(250), nullable=False)
  main_img = db.Column(db.String(250), nullable=False)
  project_img = db.Column(db.String(250), nullable=False)
  github_link = db.Column(db.String(250))
  website_link = db.Column(db.String(250))

# with app.app_context():
#     db.create_all()

class UserForm(FlaskForm):

  username = StringField("Username: ", validators=[DataRequired()])
  password = PasswordField("Password: ", validators=[DataRequired()])
  submit = SubmitField("Submit")


class ProjectForm(FlaskForm):

  project_type = StringField("Type (website, gui etc..): ", validators=[DataRequired()])
  title = StringField("Title: ", validators=[DataRequired()])
  sub_title = StringField("Subtitle: ", validators=[DataRequired()])
  general = StringField("Description: ", validators=[DataRequired()])
  tools = StringField("Tools: ", validators=[DataRequired()])
  languages = StringField("Languages: ", validators=[DataRequired()])
  img_main = StringField("Main Image: ", validators=[DataRequired()])
  img_project = StringField("Project Image: ", validators=[DataRequired()])
  link_github = StringField("Github Link: ", validators=[DataRequired()])
  link_website = StringField("Website Link: ")
  submit = SubmitField("Submit")



@app.route('/')
def home():
  projects = Project.query.all()
  return render_template('index.html', title="Home", projects=projects)


@app.route('/portfolio/<project_id>', methods=['GET', 'POST'])
def portfolio_page(project_id):
  project = Project.query.get_or_404(project_id)
  projects = [item for item in Project.query.all() if item.id != project.id]
  return render_template('portfolio_item.html', title="Portfolio", project=project, projects=projects)


@app.route('/user/login', methods=['GET', 'POST'])
def login():
  form = UserForm()
  if form.validate_on_submit():
    print(form.username.data)
    print(form.password.data)
    user = User.query.filter_by(user_name=form.username.data).first()
    print(user)
    if not user or (user and not user.check_password(form.password.data)):
      flash("Wrong username or password")
    else:
      login_user(user)
      flash(f'{user.user_name} logged in.')
      next = request.args.get('next')
      if not next or url_parse(next).netloc != '':
          next = url_for('home')
      return redirect(next)

  return render_template("user_form.html", form=form, title="Login")


@app.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
  form = UserForm()
  if form.validate_on_submit():
    user = User.query.filter_by(user_name=form.username.data).first()
    if user:
      flash("Username already taken. Please choose another.")
    else:
      user = User()
      user.user_name = form.username.data
      user.set_password(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash(f'{user.user_name} created.')
      return redirect(url_for('home'))

  return render_template("user_form.html", form=form, title="Create User")


@app.route('/project/create', methods=['GET', 'POST'])
@login_required
def create_project():
  form = ProjectForm()
  if form.validate_on_submit():
    project = Project.query.filter_by(title=form.title.data).first()
    if project:
      flash("Title already used. Please choose another.")
    else:
      project = Project()
      project.project_type = form.project_type.data
      project.title = form.title.data
      project.sub_title = form.sub_title.data
      project.project_general = form.general.data
      project.project_tools = form.tools.data
      project.project_languages = form.languages.data
      project.main_img = form.img_main.data
      project.project_img = form.img_project.data
      project.github_link = form.link_github.data
      project.website_link = form.link_website.data
      db.session.add(project)
      db.session.commit()
      flash(f'{project.title} created.')
      return redirect(url_for('home'))

  return render_template("project_form.html", form=form, title="Create User")


@app.route('/project/edit/<project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
  form = ProjectForm()
  project = Project.query.get_or_404(project_id)
  if not project:
    flash("Project not found")
    return redirect(url_for('home'))
  if form.validate_on_submit():
    project.project_type = form.project_type.data
    project.title = form.title.data
    project.sub_title = form.sub_title.data
    project.project_general = form.general.data
    project.project_tools = form.tools.data
    project.project_languages = form.languages.data
    project.main_img = form.img_main.data
    project.project_img = form.img_project.data
    project.github_link = form.link_github.data
    project.website_link = form.link_website.data
    db.session.commit()
    flash("Project Updated")
    return redirect(url_for('portfolio_page', project_id=project.id))
  elif request.method == 'GET':
    form.project_type.data = project.project_type
    form.title.data = project.title
    form.sub_title.data = project.sub_title
    form.general.data = project.project_general
    form.tools.data = project.project_tools
    form.languages.data = project.project_languages
    form.img_main.data = project.main_img
    form.img_project.data = project.project_img
    form.link_github.data = project.github_link
    form.link_website.data = project.website_link
  return render_template('project_form.html', title="Edit Project", form=form)


@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
  app.run(debug=True)


# ########################### #
# REGISTER CODE FOR USER_PAGE #
# ########################### #
# user = User()
#     user.user_name = form.username.data
#     user.set_password(form.password.data)
#     db.session.add(user)
#     db.session.commit()