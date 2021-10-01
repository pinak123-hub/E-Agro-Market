from flask import Flask, render_template,request,redirect,flash,session
import json
import os
from werkzeug.utils import secure_filename
import random
from flask_mail import Mail
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flaskwebgui import FlaskUI



with open('config/config.json', 'r') as c:
    param=json.load(c)['params']
app=Flask(__name__)
ui = FlaskUI(app)
app.config['upload_folder']=param['upload_location']
app.config.update(
MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = param['gmail-user'],
    MAIL_PASSWORD=  param['gmail-password']
)
mail = Mail(app)

#database server configuration

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if(param['local_server']):
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['prod_uri']
db = SQLAlchemy(app)



# farmmer_database_signup
class farmer_signup(db.Model):
    sr_no=db.Column(db.Integer, unique=True,primary_key=True)
    fname = db.Column(db.String(80), unique=False, nullable=False)
    lname = db.Column(db.String(80), unique=False, nullable=False)
    uname = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    dob = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)



# merchant_database_signup
class signup(db.Model):
    sr_no = db.Column(db.Integer, unique=True, primary_key=True)
    fname = db.Column(db.String(80), unique=False, nullable=False)
    lname = db.Column(db.String(80), unique=False, nullable=False)
    uname = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    dob = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(80), unique=False, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    gstn = db.Column(db.String(80), unique=False, nullable=False)

# products database
class product(db.Model):
    sr_no = db.Column(db.Integer, unique=True, primary_key=True)
    username= db.Column(db.String(80), unique=False, nullable=False)
    productname = db.Column(db.String(80), unique=False, nullable=False)
    quantity = db.Column(db.String(80), unique=False, nullable=False)
    contact_no= db.Column(db.String(120), unique=False, nullable=False)
    price = db.Column(db.String(120), unique=False, nullable=False)
    fullname = db.Column(db.String(120), unique=False, nullable=False)
    cur_date = db.Column(db.String(120), unique=False, nullable=True)
    photo = db.Column(db.String(120), unique=False, nullable=True)

# home
@app.route('/')
def home():
    return render_template('index.html')




# farmer_login
@app.route('/farmer_login', methods=['GET', 'POST'])
def farmer_login():
    if 'user' in session:
        return redirect('/farmer_dashboard')
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        login=signup.query.filter_by(uname=username).first()
        try:
            if (login.uname == username ):
                if (login.password == password):
                    session['user'] = username
                    return redirect('/farmer_dashboard')
                else:
                    flash("wrong password, Please enter proper password", "danger")
                    return render_template('farmer_login.html', head=param['head2'])

        except:
            flash("user not found please signup", "danger")
            return render_template('farmer_login.html', head=param['head2'])

    return render_template('farmer_login.html')




#dashboard_farmer
@app.route('/farmer_dashboard')
def dashboard_farmer():
    if 'user' in session:
        user_name = session['user']
        results = product.query.filter_by(username=user_name).all()
        return render_template('/dashboard.html', results=results, username=user_name)



#add new product
@app.route('/farmer_dashboard/add_new_product', methods=['GET','POST'])
def add_new_product():
    if 'user' in session:
        u_name=session['user']
        if request.method=='POST':
            username = request.form.get('username')
            productname = request.form.get('productname')
            quantity = request.form.get('quantity')
            contact_no = request.form.get('contact_no')
            price = request.form.get('price')
            fullname = request.form.get('fullname')
            photo=request.form.get('photo')
            f=request.files['photo']
            f.save(os.path.join(app.config['upload_folder'], secure_filename(f.filename)))
            entry = product(username=username, productname=productname, quantity=quantity, contact_no=contact_no, price=price, fullname=fullname, cur_date=datetime.now(), photo=f.filename)
            db.session.add(entry)
            db.session.commit()
            return redirect('/farmer_dashboard')
    return render_template('add_new_product.html', u_name=u_name)

@app.route('/farmer_dashboard/delete/<string:cur_date>')
def delete(cur_date):
    if 'user' in session:
        u_name=session['user']
        product1=product.query.filter_by(cur_date=cur_date, username=u_name).first()
        file=param['upload_location']+product1.photo
        if os.path.exists(file):
            os.remove(file)
        db.session.delete(product1)
        db.session.commit()
        return redirect('/farmer_dashboard')


#logout_farmer
@app.route('/logout')
def logout_farmer():
    session.pop('user')
    return redirect('/farmer_login')




#farmer_signup
@app.route('/farmer_signup', methods=['GET', 'POST'])
def farmer_signup1():
    if(request.method=='POST'):
        fname=request.form.get('first_name')
        lname=request.form.get('last_name')
        uname=request.form.get('username')
        address=request.form.get('address')
        email=request.form.get('email')
        dob=request.form.get('DOB')
        gender=request.form.get('gender')
        password=request.form.get('Password')
        conf_password = request.form.get('Confirm_Password')
        # error_msg = 'please enter proper password'


        if(password==conf_password):
            entry = farmer_signup(fname=fname, lname=lname, uname=uname, address=address, email=email, dob=dob,gender=gender, password=password)
            db.session.add(entry)
            db.session.commit()
            try:
                entry = farmer_signup(fname=fname, lname=lname, uname=uname, address=address, email=email, dob=dob,
                                      gender=gender, password=password)
                db.session.add(entry)
                db.session.commit()
            except:
                flash("username or Email ID already taken please enter other username", "warning")
                return render_template('farmer_signup.html', head=param['head'])
            else:
                flash("you have successfully created account . please, goto login page to login into your account",
                      "success")

                return render_template('farmer_signup.html', head=param['head1'])
        else:
            flash("you have entered wrong confirmation password...!", "danger")
            return render_template('farmer_signup.html', head=param['head2'] )


    return render_template('farmer_signup.html')




# merchant_login
@app.route('/merchant_login', methods=['GET', 'POST'])
def merchant_login():
    if 'user_merchant' in session:
        return redirect('/merchant_dashboard')
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        login=signup.query.filter_by(uname=username).first()
        try:
            if (login.uname == username):
                if (login.password == password):
                    session['user_merchant'] = username
                    return redirect('/merchant_dashboard')
                else:
                    flash("wrong password, Please enter proper password", "danger")
                    return render_template('merchant_login.html', head=param['head2'])
        except:
            flash("user not found please signup", "danger")
            return render_template('merchant_login.html', head=param['head2'])

    return render_template('merchant_login.html')




#dashboard_merchant
@app.route('/merchant_dashboard', methods=['GET', 'POST'])
def dashboard_merchant():
    user_name = session['user_merchant']
    if request.method=='POST':
        search=request.form.get('search')
        results = product.query.filter_by(productname=search).all()
        return render_template('dashboard_merchant.html', results=results, username=user_name)
    return render_template('dashboard_merchant.html', username=user_name)



@app.route('/merchant_dashboard/view/<string:cur_date>')
def view_merchant_image(cur_date):
    if 'user_merchant' in session:
        user_name = session['user_merchant']
        try:
            res=product.query.filter_by(cur_date=cur_date).first()
            return render_template('image.html', result=res,username=user_name)
        except:
            flash("May be product has been deleted...!", "warning")
            return render_template('dashboard_merchant.html', username=user_name,head=param['head3'])

@app.route('/farmer_dashboard/view/<string:cur_date>')
def view_farmer_image(cur_date):
    if 'user' in session:
        user_name = session['user']
        res=product.query.filter_by(cur_date=cur_date).first()
        return render_template('image_farmer.html', result=res,username=user_name)


@app.route('/logout_merchant')
def logout_merchant():
    session.pop('user_merchant')
    return redirect('/merchant_login')



#merchant_signup
@app.route('/merchant_signup', methods=['GET', 'POST'])
def merchant_signup1():


    if (request.method == 'POST'):
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        uname = request.form.get('username')
        address = request.form.get('address')
        email = request.form.get('email')
        dob = request.form.get('DOB')
        gender = request.form.get('gender')
        password = request.form.get('Password')
        conf_password = request.form.get('Confirm_Password')
        gstn=request.form.get('gstn')

        if (password == conf_password):
            try:
                entry = signup(fname=fname, lname=lname, uname=uname, address=address, email=email, dob=dob,
                                      gender=gender, password=password, gstn=gstn)
                db.session.add(entry)
                db.session.commit()
            except:
                flash("username or Email ID already taken please enter other username", "warning")
                return render_template('merchant_signup.html',head= param['head'])
            else:
                flash("you have successfully created account . please, goto login page to login into your account",
                      "success")
                return render_template('merchant_signup.html', head=param['head1'])
        else:
            flash("you have entered wrong confirmation password...!", "danger")
            return render_template('merchant_signup.html', head=param['head2'])

    return render_template('/merchant_signup.html')



#about us
@app.route('/about')
def about():
    return render_template('about.html')


#contact us
@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        subject=request.form.get('subject')
        msg=request.form.get('msg')
        mail.send_message( 'name: ' + name + ' Email ID:' + email +  ' Topic :' + subject,sender=msg,recipients=[param['gmail-user']],body=msg )
        flash("you have successfully semd the message. We will replay you under 24hrs.",
              "success")
        return render_template('contact_us.html', head=param['head1'])

    return render_template('contact_us.html')


#forgot_password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method=='POST':
        username=request.form.get('username')
        res = signup.query.filter_by(uname=username).first()
        try:
            if(res.uname==username):
                session['username'] = res.uname
                otp=random.randrange(100000,999999)
                session['otp'] = str(otp)
                msg="your OTP is" + str(otp)
                mail.send_message('verification otp ....!' ,sender=param['gmail-user'],recipients=[res.email],body=msg)
                return redirect('/otp_verification')
        except:
            flash("username not found.. please create account or Enter proper username...","danger")
            return render_template('forgot_password.html', head=param['head2'])
    return render_template('forgot_password.html')

#otp_verify
@app.route('/otp_verification', methods=['GET','POST'])
def otp_verification():
    otp=session.get('otp')
    print(otp)
    if request.method=='POST':
        otp_page=request.form.get('otp')
        print(otp_page)
        if otp_page==otp:
            return redirect('/new_password')
        else:
            flash("wrong otp please enter again...", "warning")
            return render_template('otp_verify.html', head=param['head2'])

    flash("OTP has been send successfully, Check your mailbox and enter otp in below filed...", "success")
    return render_template('otp_verify.html', head=param['head1'])

#new_password
@app.route('/new_password', methods=['GET','POST'])
def new_password():
    if request.method=='POST':
        password=request.form.get('password')
        conf_password=request.form.get('conf_password')
        if password==conf_password:
            update=signup.query.filter_by(uname=session['username']).first()
            update.password=password
            db.session.commit()
            flash("New password set Successfully Goto login page to login your account..Thank you","success")
            return render_template('enter_new_password.html', head=param['head1'])
        else:
            flash("your password and confirmation passwords are not same... Please Enter Same password in both the Fields..", "warning")
            return render_template('enter_new_password.html', head=param['head2'])
    flash("OTP verified successfully", "success")
    return render_template('enter_new_password.html', head=param['head1'])





#forgot_username
@app.route('/username_forgot', methods=['GET', 'POST'])
def forgot_username():
    if request.method=='POST':
        email=request.form.get('email')
        res=signup.query.filter_by(email=email).first()
        try:
            if res.email==email:
                msg = "your username of E-AGRO-MARKET login is :   " + str(res.uname)
                mail.send_message('E-AGRO-MARKET', sender=param['gmail-user'], recipients=[res.email], body=msg)
                flash("Username has been send successfully goto check your mailbox and login.... Thank you", "success")
                return render_template('username_forgot.html', head=param['head1'])
        except:
            flash("wrong Email ID entered....Please enter proper Email ID..","danger")
            return render_template('username_forgot.html', head=param['head2'])
    return render_template('username_forgot.html')

# main_function
if __name__ == '__main__':
    app.secret_key = 'mykey'
    app.run()
