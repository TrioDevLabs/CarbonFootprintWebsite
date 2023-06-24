from datetime import datetime
import secrets
from flask import Flask, flash, render_template, request, redirect, url_for, session, current_app
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegisterationForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Initialization and Configuration

app = Flask(__name__)
app.config.from_pyfile('config.py')

# Additional Libraries and Features

mail = Mail(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please login to access this page.'


class Users(db.Model, UserMixin):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable=False, unique=True)
    PasswordHash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    SecurityCode = db.Column(db.String(255))
    Confirmed = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.current_timestamp())

    @property
    def id(self):
        return str(self.UserID)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False


class UserSessions(db.Model):
    SessionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    LoginTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    LogoutTime = db.Column(db.DateTime)


class TwoFactorAuth(db.Model):
    AuthID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    OTP = db.Column(db.String(6))
    ExpiryTime = db.Column(db.DateTime)


class HouseholdUsage(db.Model):
    UsageID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    PropaneUsage = db.Column(db.Float)
    NaturalGasUsage = db.Column(db.Float)
    ElectricityUsage = db.Column(db.Float)
    FuelOilUsage = db.Column(db.Float)
    MonthYear = db.Column(db.Date)


class Vehicles(db.Model):
    VehicleID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    NumberOfVehicles = db.Column(db.Integer)
    AverageMilesDriven = db.Column(db.Float)
    AverageMileage = db.Column(db.Float)
    MonthYear = db.Column(db.Date)


class VehicleDetails(db.Model):
    VehicleDetailID = db.Column(db.Integer, primary_key=True)
    VehicleID = db.Column(db.Integer, db.ForeignKey('Vehicles.VehicleID'))
    MilesDriven = db.Column(db.Float)
    Mileage = db.Column(db.Float)
    MonthYear = db.Column(db.Date)


class Waste(db.Model):
    WasteID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    AluminumSteelCans = db.Column(db.Float)
    Plastic = db.Column(db.Float)
    Glass = db.Column(db.Float)
    Newspaper = db.Column(db.Float)
    Magazines = db.Column(db.Float)
    MonthYear = db.Column(db.Date)

# DB Relations


sessions = db.relationship('UserSession', backref='Users')
two_factor_auths = db.relationship('TwoFactorAuth', backref='Users')
household_usages = db.relationship('HouseholdUsage', backref='Users')
vehicles = db.relationship('Vehicles', backref='Users')
vehicledetail = db.relationship('VehicleDetails', backref='Vehicles')
wastes = db.relationship('Waste', backref='Users')

# Page Routing

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.before_request
def before_request():
    if not getattr(current_app, "user_loaded", False) and "user" in session:
        email = session["user"]
        user = Users.query.filter_by(email=email).first()
        if user:
            login_user(user)
            current_app.user_loaded = True

@app.route("/", methods=['GET', 'POST'])
def home_page():
    print(current_user)
    return render_template('index.html')


@app.route('/loginUser', methods=['GET', 'POST'])
def login():
    form = RegisterationForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password = str(password)
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.PasswordHash, password):
            session['email'] = email
            return redirect(url_for('verify_2fa'))

        else:
            flash('Login Unsuccessful. Please check email and password',
                  category='danger')

    return render_template('login-signup-page.html', mode="Login", form=form)


@app.route('/registerUser', methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if request.method == 'POST':
        if form.validate():
            username = request.form.get('username')
            email_address = request.form.get('email_address')
            password = generate_password_hash(
                str(request.form.get('password')))
            p1 = str(request.form.get('password'))
            p2 = str(request.form.get('confirmPassword'))
            if p1 == p2:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                user = Users(Username=username,
                             email=email_address, PasswordHash=password, CreatedAt=timestamp, Confirmed=False)
                db.session.add(user)
                db.session.commit()
                session['newRegistrationEmail'] = email_address
                
                return redirect(url_for('confirm_email'))
            else:
                flash('Passwords do not match', category='danger')

        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(
                    f'Error Creating User: {err_msg}', category='danger')
        return render_template('login-signup-page.html', mode="Signup", form=form)

    return render_template('login-signup-page.html', mode="Signup", form=form)


@app.route('/confirm_email', methods=['GET', 'POST'])
def confirm_email():
    email = session['newRegistrationEmail']
    user = Users.query.filter_by(email=email).first()
    if request.method == 'POST':
        security_code = request.form.get('1') + request.form.get('2') + request.form.get('3') + request.form.get('4') + request.form.get('5') +request.form.get('6')
        if user and user.SecurityCode == security_code:
            db.session.commit()
            user.Confirmed = True
            db.session.commit()
            flash('User registered successfully.', category='info')
            return redirect(url_for('login'))
        else:
            flash('Invalid email or security code', category='error')
    else:
        security_code = secrets.token_hex(3)
        user.SecurityCode = security_code
        db.session.commit()
        msg = Message(
            'Confirm your email', sender='your-email@example.com', recipients=[email])
        msg.body = f'Your confirmation code is: {security_code}'
        mail.send(msg)

    return render_template('confirm_email.html', email=email)

@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    email = session['email']
    user = Users.query.filter_by(email=email).first()
    
    if request.method == 'POST':
        security_code = request.form.get('1') + request.form.get('2') + request.form.get('3') + request.form.get('4') + request.form.get('5') +request.form.get('6')

        if user and user.SecurityCode == security_code:
            session['logged_in'] = True
            login_user(user)
            session["user"] = user.email

            return render_template('index.html')
        
    else:
        security_code = secrets.token_hex(3)
        user.SecurityCode = security_code
        db.session.commit()
        msg = Message('2FA Security Code',
                        sender='your-email@example.com', recipients=[email])
        msg.body = f'Your 2FA security code is: {security_code}'
        mail.send(msg)

    return render_template('verify_2fa.html', email=email)

@app.route('/logout')
def logout():
    if "user" in session:
        session.pop("user", None)
        logout_user()
        flash('You have been logged out', category='success')
        return render_template('index.html')

    else:
        flash('You are not logged in', category='success')
        return redirect(url_for('login'))
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cfc')
def cfc():
    return render_template('cfc.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Error Routing


@app.errorhandler(404)
def invalid_route(e):
    return render_template('page-404.html')


@app.errorhandler(500)
def invalid_route(e):
    return render_template('page-500.html')

# Run Application

def exec_app():
    if __name__ == "app.app":
        app.run(debug=True)
