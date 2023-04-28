from my_website import app,bcrypt,db
from flask import redirect,url_for,render_template
from flask_login import login_user,LoginManager,login_required,logout_user
from data_base import Authority
from flask_wtf import FlaskForm
from wtforms import EmailField,PasswordField,SubmitField,SelectField
from wtforms.validators import InputRequired, Length,Email

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



class Register_form(FlaskForm):
    user_id     = EmailField(validators=[InputRequired(),Length(min=9,max=30),Email()], render_kw={"placeholder":"User_email"})
    password    = PasswordField(validators=[InputRequired(),Length(min=8,max=20)], render_kw={"placeholder":"Password"})
    role        = SelectField(validators=[InputRequired()], choices=[('VIEWER', 'Viewer'), ('ADMIN', 'Admin')])
    submit      = SubmitField('Register')

    def validate_user_id(self,user_id):
        with app.app_context():
            existing_user_user_id = Authority.query.filter_by(user_id = user_id.data)
        if existing_user_user_id:
            app.logger.info("User already Exist with this username.")
            return False
        else:
            app.logger.info("User user created in Authority.")
            return True
        
class Login_form(FlaskForm):
    user_id     = EmailField(validators=[InputRequired(),Length(min=9,max=30),Email()], render_kw={"placeholder":"User_email"})
    password    = PasswordField(validators=[InputRequired(),Length(min=8,max=20)], render_kw={"placeholder":"Password"})
    submit      = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return Authority.query.get(user_id)
    
@app.route('/login',methods = ['GET','POST'])
def login():
    form = Login_form()
    if form.validate_on_submit():
        with app.app_context():
            user = Authority.query.filter_by(user_id = form.user_id.data).first()
        if user:
            if bcrypt.check_password_hash(user.password.encode('utf-8'),form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('Admin/login.html',form = form)

@app.route('/dashboard',methods = ['GET','POST'])
@login_required
def dashboard():
    return render_template('Admin/homepage.html')

@app.route('/logout',methods = ['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register',methods = ['GET','POST'])
def register():
    form = Register_form()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = Authority(user_id = form.user_id.data,
                             password = hashed_password.decode('utf-8'),
                             role = form.role.data)
        try:
            with app.app_context():
                db.session.add(new_user)
                db.session.commit()
        except Exception as e:
            app.logger.error(f"Error while inserting user in Authority.-> {e}")
        return redirect(url_for('login'))
    return render_template('Admin/signup.html',form=form)
        

    
