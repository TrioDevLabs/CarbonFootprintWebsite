from datetime import datetime
import secrets
import cryptography
from flask import Flask, flash, render_template, request, redirect, url_for, session, current_app
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegisterationForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import aliased

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
    __tablename__ = 'users'
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
    __tablename__ = 'usersessions'
    SessionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    LoginTime = db.Column(db.DateTime, default=db.func.current_timestamp())
    LogoutTime = db.Column(db.DateTime)


class TwoFactorAuth(db.Model):
    __tablename__ = 'twofactorauth'
    AuthID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    OTP = db.Column(db.String(6))
    ExpiryTime = db.Column(db.DateTime)


class HouseholdUsage(db.Model):
    __tablename__ = 'householdusage'
    UsageID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer )
    PropaneUsage = db.Column(db.Float)
    NaturalGasUsage = db.Column(db.Float)
    ElectricityUsage = db.Column(db.Float)
    FuelOilUsage = db.Column(db.Float)
    Emissions = db.Column(db.Float)
    MonthYear = db.Column(db.Date)


class Vehicles(db.Model):
    __tablename__ = 'vehicles'
    EntryID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    NumberOfVehicles = db.Column(db.Integer)
    AverageMilesDriven = db.Column(db.Float)
    AverageMileage = db.Column(db.Float)
    Emissions = db.Column(db.Float)
    MonthYear = db.Column(db.Date)


class Waste(db.Model):
    __tablename__ = 'waste'
    Entry_ID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer)
    AluminumSteelCans = db.Column(db.Boolean)
    Plastic = db.Column(db.Boolean)
    Glass = db.Column(db.Boolean)
    Newspaper = db.Column(db.Boolean)
    Magazines = db.Column(db.Boolean)
    MonthYear = db.Column(db.Date)
    Emissions = db.Column(db.Float)

# DB Relations





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
        print(security_code,"kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
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

@app.route('/cfc', methods=['GET', 'POST'])
@login_required
def cfc():
    email = session['email']
    user = Users.query.filter_by(email=email).first()
    print(user)
    print(email)
    waste_emissions= 3458
    gas_emissions=0
    elect_emissions=0
    oil_emissions=0
    propane_emissions=0
    vehicleNum=0
    vehicle_emissions=[0,0,0,0,0,0]
    vehicle_emissions_total=0
    UserId = current_user.UserID
    current_date = datetime.now().date()  # Get the current date
    formatted_date = current_date.strftime('%Y-%m-%d')
    if request.method == 'POST':
        type=request.form.get("type")
        gas=request.form.get("gas")
        if (gas!=""):
            gas=float(gas)
        
        using_gas = False
        using_electricity = False
        using_propane = False
        using_oil = False
        
        gas_type=request.form.get("gas_type")
        if (gas_type=="Thousand Cubic Feet"):
            gas_emissions = (gas * 119.58) * 12
            using_gas = True
            # convert gas to therms
            gas = gas * 10.36

        elif (gas_type=="Therm"):
            gas_emissions = (gas / 11.7) * 12
            using_gas = True
        elif (gas_type=="Dollars"):
            gas_emissions = (gas / 10.68) * 119.58 * 12
            using_gas = True
            # convert gas to therms
            gas= gas / 0.95
        electricity=request.form.get("electricity")
        if (electricity!=""):
            electricity=float(electricity)
        elect_type=request.form.get("elec_type")
        if (elect_type=="kWh"):
            elect_emissions = (electricity * 18.42) + 12
            using_electricity = True
        elif (elect_type=="Dollars"):
            elect_emissions = (electricity / 0.1188) * 18.42 * 12
            using_electricity = True
            # convert electricity to kWh
            electricity = electricity * 7.76
        oil=request.form.get("oil")
        if (oil!=""):
            oil=float(oil)
        oil_type=request.form.get("oil_type")
        if (oil_type=="Gallons"):
            using_oil = True
            oil_emissions =  (oil / 4.02) * 22.61 * 12
        elif (oil_type=="Dollars"):
            using_oil   = True
            oil_emissions = (oil) * 22.61 * 12
            # convert oil to gallons
            oil = oil * 0.14

        propane=request.form.get("propane")
        if (propane!=""):
            propane=float(propane)
        propane_type=request.form.get("propane_type")
        if (propane_type=="Gallons"):
            using_propane = True
            propane_emissions =  (propane) * 12.43 * 12
        elif (propane_type=="Dollars"):
            using_propane = True
            propane_emissions = (propane / 2.47) * 12.43 * 12
            # convert propane to gallons
            propane = propane *0.37

        
        if(using_gas or using_propane or  using_electricity or using_oil):
            if(using_gas):
                gas = gas
                gas_emissions = gas_emissions
            else:
                gas_emissions = 0
                gas = 0
            if(using_electricity):
                electricity = electricity
                elect_emissions = elect_emissions
            else:
                electricity = 0
                elect_emissions = 0
            if(using_oil):
                oil = oil
                oil_emissions = oil_emissions
            else:
                oil = 0
                oil_emissions = 0
            if(using_propane):
                propane = propane
                propane_emissions = propane_emissions
            else:
                propane = 0
                propane_emissions = 0
            total_emissions = gas_emissions + elect_emissions + oil_emissions + propane_emissions
            HouseOrder =HouseholdUsage(UserID=UserId, PropaneUsage=propane,NaturalGasUsage=gas,ElectricityUsage=electricity,FuelOilUsage=oil,MonthYear=formatted_date,Emissions=total_emissions)
            db.session.add(HouseOrder)
            db.session.commit()
                
        
        
        vehicleNum=request.form.get("vehicleNum")
        vehicleNum=int(vehicleNum)  
        vehicle_type=request.form.get("vehicle_type")
        
       
        avg_car_milage = 0
        avg_car_miles = 0
        is_vehicles = False
        if (vehicleNum > 0):
            is_vehicles = True

        for i in range(1,vehicleNum+1):
            milesInput=request.form.get("miles"+str(i))
            milesInput=float(milesInput)
            mileageInput=request.form.get("mileage"+str(i))
            mileageInput=float(mileageInput)
            if (vehicle_type=="Yes"):
                vehicle_emissions[i] = (milesInput / mileageInput) * 19.6 * 1.01

            else:
                vehicle_emissions[i] = (milesInput /mileageInput) * 19.6 * 1.01
                vehicle_emissions[i] = vehicle_emissions[i] + vehicle_emissions[i] * (1/10)
            avg_car_milage = avg_car_milage + mileageInput
            avg_car_miles = avg_car_miles + milesInput    
        
        for i in range(1,vehicleNum+1):
            vehicle_emissions_total=vehicle_emissions_total+vehicle_emissions[i]
        
        avg_car_miles = avg_car_miles / vehicleNum
        avg_car_milage = avg_car_milage / vehicleNum
        
        if (is_vehicles):
            VehicleOrder = Vehicles(UserID=UserId,NumberOfVehicles=vehicleNum,AverageMilesDriven=avg_car_miles,AverageMileage=avg_car_milage,MonthYear=formatted_date,Emissions=vehicle_emissions_total)
            db.session.add(VehicleOrder)
            db.session.commit()

        # check if user is in a session
        # adee puth the queries here plis




        aluminium = request.form.get("aluminium")
        plastic = request.form.get("plastic")
        glass = request.form.get("glass")
        newspaper = request.form.get("newspaper")
        magazines = request.form.get("magazines")

        if (aluminium):
            waste_emissions = waste_emissions - 447
            aluminium = True
        else:
            aluminium = False
        if (plastic):
            waste_emissions = waste_emissions - 178
            plastic = True
        else:
            plastic = False
        if (glass):
            waste_emissions = waste_emissions - 127
            glass = True
        else:
            glass = False
        if (newspaper):
            waste_emissions = waste_emissions - 566
            newspaper = True
        else:
            newspaper = False
        if (magazines):
            waste_emissions = waste_emissions - 137
            magazines = True
        else:
            magazines = False


        print(magazines, newspaper, glass, plastic, aluminium,"lllllllllllllllllllllllllllllllllll")

        
        waste_order=Waste(UserID=UserId,AluminumSteelCans=aluminium,Plastic=plastic,Glass=glass,Newspaper=newspaper,Magazines=magazines,MonthYear=formatted_date,Emissions=waste_emissions)
        db.session.add(waste_order)
        db.session.commit()


    return render_template('cfc.html',gas_emissions=gas_emissions,elect_emissions=elect_emissions,oil_emissions=oil_emissions,propane_emissions=propane_emissions
                           ,vehicle_emissions=vehicle_emissions
                           ,vehicle_emissions_total=vehicle_emissions_total
                           ,waste_emissions=waste_emissions)
    
@app.route('/contact')
def contact():
    return render_template('contact.html')



@app.route('/homerecord')
def homerecord():
    household=[]
    total_usage=[]
    if current_user.is_authenticated:
        user_id = current_user.UserID
        hu = aliased(HouseholdUsage)

        household_query = db.session.query(hu).filter(hu.UserID == user_id).all()
        for household_usage in household_query:
            print(household_usage.UsageID, household_usage.PropaneUsage, household_usage.NaturalGasUsage)
            household.append(household_usage.MonthYear)
            household.append(household_usage.PropaneUsage)
            household.append(household_usage.NaturalGasUsage)
            household.append(household_usage.ElectricityUsage)
            household.append(household_usage.FuelOilUsage)
            household.append(household_usage.Emissions)
            total_usage.append(household)
            household=[]
    return render_template('homerecord.html',usage=total_usage)



@app.route('/vehiclerecord')
def vehiclerecord():
    vehicles=[]
    total_usage=[]
    if current_user.is_authenticated:
        user_id = current_user.UserID
        v = aliased(Vehicles)


        # Query to retrieve Vehicles entries where UserID is the same
        vehicles_query = db.session.query(v).filter(v.UserID == user_id).all()
        for vehicle in vehicles_query:
            vehicles.append(vehicle.MonthYear)
            vehicles.append(vehicle.NumberOfVehicles)
            vehicles.append(vehicle.AverageMilesDriven)
            vehicles.append(vehicle.AverageMileage)
            vehicles.append(vehicle.Emissions)
            total_usage.append(vehicles)
            vehicles=[]

    return render_template('vehiclerecord.html',usage=total_usage)


@app.route('/wasterecord')
def wasterecord():
    waste_material=[]
    total_usage=[]
    if current_user.is_authenticated:
        user_id = current_user.UserID
        w = aliased(Waste)


        # Query to retrieve Vehicles entries where UserID is the same
        waste_query = db.session.query(w).filter(w.UserID == user_id).all()
        for waste in waste_query:
            waste_material.append(waste.MonthYear)
            waste_material.append(waste.AluminumSteelCans)
            waste_material.append(waste.Plastic)
            waste_material.append(waste.Glass)
            waste_material.append(waste.Newspaper)
            waste_material.append(waste.Magazines)
            waste_material.append(waste.Emissions)
            total_usage.append(waste_material)
            waste_material=[]

    return render_template('wasterecord.html',usage=total_usage)
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
