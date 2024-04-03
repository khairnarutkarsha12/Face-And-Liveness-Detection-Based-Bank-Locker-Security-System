# import the necessary packages
from utils import *
from xmlrpc.client import boolean
from flask import Flask, render_template, redirect, url_for, request, session, Response, flash
#from flask import *
from flask_wtf import FlaskForm, RecaptchaField
from flask_recaptcha import ReCaptcha
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from password_strength import PasswordPolicy
from password_strength import PasswordStats
from datetime import datetime
from markupsafe import Markup
from werkzeug.utils import secure_filename
import os
import cv2

import pandas as pd
from playsound import playsound
import sqlite3
from flask_mail import Mail, Message
# from arduino import *


username=''
password=''
email=''
locker=''
login_time=''
max_attempt = 4

server_mail = 'mail.eternalgig.com'
port = 465
sender_email = 'bankadmin@eternalgig.com'
sender_password = 'B7u~O5+xmRl-'

app = Flask(__name__)

#password_strength
policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    strength=0.10 # need a password that scores at least 0.5 with its entropy bits
)
app.config['SECRET_KEY'] = '@#$%^&*('
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfUsq4fAAAAAO9ERpTCU9xMvgHRr_hOtN1rt8iN'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfUsq4fAAAAANMh390iAUkCSojV4r3Y2HdlQvXw'

class MyForm(FlaskForm):
    recaptcha = RecaptchaField()

@app.route('/', methods=['GET', 'POST'])
def input():
	form = MyForm()
	error = None
	if request.method == 'POST':
		username=request.form['username']
		password=request.form['password']

		stats = PasswordStats(password)
		checkpolicy = policy.test(password)
		
		if stats.strength() < 0.10:
			print(stats.strength())
			flash("Password not strong enough. Avoid consecutive characters and easily guessed words.")
			return render_template('input.html')
	
	
		if request.form['username'] != 'admin' or request.form['password'] != 'Admin@123' or not form.validate_on_submit():
			error = 'Please try again.'
		else:
			return redirect(url_for('home'))

	return render_template('input.html', form=form, error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = MyForm()
    
	global username
	global password
	global locker
	
	global nominee
	message = ""
	error = ""
	
	if request.method=='POST':
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']
		
		nominee = request.form['nominee']

		stats = PasswordStats(password)
		checkpolicy = policy.test(password)
		
		if stats.strength() < 0.10:
			print(stats.strength())
			flash("Password not strong enough. Avoid consecutive characters and easily guessed words.")
			return render_template('register.html')
		
		#if request.method == 'POST': # Check to see if flask.request.method is POST
		# if form.validate_on_submit(): # Use verify() method to see if ReCaptcha is filled out
		# 	message = 'Thanks for filling out the form!' # Send success message
		# else:
		# 	message = 'Please try again!' # Send error message
		# 	return redirect(url_for('register',message=message))
    #return render_template('index.html', message=message)
		
		return redirect(url_for('register1'))
		
	return render_template('register.html',form=form,message=message,error=error)

@app.route('/register1', methods=['GET', 'POST'])
def register1():
	global username
	global password
	global locker
	global email
	global nominee
	global login_time
	error=''
	
	if request.method=='POST':

			username = request.form['username']
			password = request.form['password']
			locker = request.form['locker']
			email = request.form['email']
			nominee = request.form['nominee']

			d = datetime.now()
			login_time = d.strftime("%d/%m/%y,%H:%M:%S")

			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (UserName text, email text, Password text, Locker text, Nominee text, Time text, Counter int, Status text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?,?)",(username,email,password,locker,nominee,login_time,0,"Active"))
			con.commit()

			img = cv2.imread('static/images/test_image.jpg')
			cv2.imwrite('dataset/'+username+'.'+locker+'.jpg', img)

			receiver_email = email

			message = MIMEMultipart("alternative")
			message["Subject"] = "Register Done."
			message["From"] = sender_email
			message["To"] = receiver_email

			html = """\
						<html>
						<body>
							<p>Hello, From Banklocker<br>
							You are Successfully Register<br>
							<a href="127.0.0.1:5000/login">Login</a>						
							</p>
						</body>
						</html>
					"""
			innermsg = MIMEText(html, "html")
			message.attach(innermsg)

			context = ssl.create_default_context()
			with smtplib.SMTP_SSL("mail.eternalgig.com", 465, context=context) as server:
				server.login(sender_email, sender_password)
				server.sendmail(
					sender_email, receiver_email, message.as_string()
				)
			return redirect(url_for('register'))

	return render_template('register1.html',username=username,password= password,locker=locker,nominee=nominee)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = MyForm()
	global username
	global password
	global locker
	error = ""

	if request.method=='POST':
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']

		con = sqlite3.connect('banklocker.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT UserName,Nominee,Counter,Status,Time from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")

		#if form.validate_on_submit(): # Use verify() method to see if ReCaptcha is filled out
		data = cursorObj.fetchone()       # Match database

		if(data and data[3]=='Active' and data[2]!=max_attempt):  # only if the data is matched and user is not blocked
			error = "Thanks for filling form...!"
			if(data[1].lower() == "nominee"):
				return redirect(url_for('login2'))
			else:
				return redirect(url_for('login1'))
		# else:
		# 	msg = Message('Hello', sender = 'rowdymaari0611@gmail.com', recipients = ['khushal.chaudhari.2001@gmail.com'])
		# 	msg.body = "This is the email body"
		# 	mail.send(msg)
		
		error = "Please try again..!!!"

		data = cursorObj.execute(f"SELECT Counter,Status,Time from Users WHERE UserName = '{username}' AND Locker = {locker}").fetchone()

		#if login fails due to wrong user credentials
		if(data):
			if(data[0] == max_attempt):                        #maximum login attempts reached

				if(data[1].split('|')[0].strip() == 'Blocked'):       #check if user is already blocked
					
					if(isReady(data[1].split('|')[1].strip())):                         #24 hours have passed
						cursorObj.execute(f"UPDATE Users SET Status = 'Active',Counter=0 WHERE UserName='{username}' AND Locker = {locker}")
						error = "  User unblocked!!!"
					else:
						error = "  Maximum attempts reached...Try after 24 hours of last fail!!!"

				else:
					d = datetime.now()
					block_time=  d.strftime("%d/%m/%y,%H:%M:%S")
					s = 'Blocked | '+ str(block_time)

					cursorObj.execute(f"UPDATE Users SET Status = '{s}' WHERE UserName='{username}' AND Locker = {locker}")
			
			else:
				current_count = cursorObj.execute(f"SELECT Counter from Users WHERE UserName = '{username}' AND Locker = {locker}").fetchone()[0]
				#current_count = (current_count+1)%max_attempt
				current_count = current_count+1
				cursorObj.execute(f"UPDATE Users SET Counter = '{current_count}' WHERE UserName='{username}' AND Locker = {locker}")
			con.commit()
		else:
			error = "User Not Register....!"
     
	return render_template('login.html',error=error)

@app.route('/login1', methods=['GET', 'POST'])
def login1():
	global username
	global password
	global locker
	global lockers
	error = ''
	
	if request.method=='POST':
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']
		
		try:
			face,blink,people,lockers = faceRecognition()		

			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT Counter from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
			current_count = cursorObj.fetchone()[0]

			'''if(face == []):
				current_count = current_count+1
				cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
				con.commit()
				error = 'Unknown Face Detected Plz Try again..!!'			
				return redirect(url_for('login',error = error))'''

			print('Detected Face:',face,blink,people)

			if(blink == 'Eye Blinking Detected..!!'):
				if(people > 1):
					error = 'Multiple Faces Detected, Plz Try again..!!'				
					
				elif(people == 0):
					error = 'No Face Detected Plz Try again..!!'				
					current_count = current_count+1

				else:
					try:
					
						if(face[0] == username):                    #Successful    Arduino
							cursorObj.execute(f"UPDATE Users SET Counter=0 WHERE UserName='{username}'")
							con.commit()
						#sendSerial("O") # temp comment
							#ARD code
							return redirect(url_for('locker'))
						else:
							# msg = Message('Hello', sender = 'rowdymaari0611@gmail.com', recipients = ['khushal.chaudhari.2001@gmail.com'])
							# msg.body = "This is the email body"
							# mail.send(msg)

							error = 'Unknown Face Detected Plz Try again..!!'					
							current_count = current_count+1

							cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
							con.commit()
					except sqlite3.Error:
						error = 'database is lock, please restart your server'

			else:
				error = 'No Live Face Found'			
				#current_count = (current_count+1)%max_attempt
				current_count = current_count+1
		except IndexError:
			error = 'face not match' 
		
	return render_template('login1.html',username=username,password= password,locker=locker,error=error)

@app.route('/nomineelogin', methods=['GET', 'POST'])
def nomineelogin():
	global username
	global password
	global locker
	global lockers
	error = ''
	
	if request.method=='POST':
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']
		
		try:
			face,blink,people,lockers = faceRecognition()		

			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT Counter from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
			current_count = cursorObj.fetchone()[0]

			'''if(face == []):
				current_count = current_count+1
				cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
				con.commit()
				error = 'Unknown Face Detected Plz Try again..!!'			
				return redirect(url_for('login',error = error))'''

			print('Detected Face:',face,blink,people)

			if(blink == 'Eye Blinking Detected..!!'):
				if(people > 1):
					error = 'Multiple Faces Detected, Plz Try again..!!'				
					
				elif(people == 0):
					error = 'No Face Detected Plz Try again..!!'				
					current_count = current_count+1

				else:
					try:
					
						if(face[0] == username):                    #Successful    Arduino
							cursorObj.execute(f"UPDATE Users SET Counter=0 WHERE UserName='{username}'")
							con.commit()
						#sendSerial("O") # temp comment
							#ARD code
							return redirect(url_for('locker'))
						else:
							# msg = Message('Hello', sender = 'rowdymaari0611@gmail.com', recipients = ['khushal.chaudhari.2001@gmail.com'])
							# msg.body = "This is the email body"
							# mail.send(msg)

							error = 'Unknown Face Detected Plz Try again..!!'					
							current_count = current_count+1

							cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
							con.commit()
					except sqlite3.Error:
						error = 'database is lock, please restart your server'

			else:
				error = 'No Live Face Found'			
				#current_count = (current_count+1)%max_attempt
				current_count = current_count+1
		except IndexError:
			error = 'face not match' 
		
	return render_template('nomineelogin.html',username=username,password= password,locker=locker,error=error)

'''@app.route('/login2', methods=['GET', 'POST'])
def login2():
	global username
	global password
	global locker
	error = ""

	if request.method=='POST':
		admin = request.form['admin']
		admin_pass = request.form['admin_pass']
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']
		
		if admin != 'admin' or admin_pass != 'Admin@123':
			error = "Please try again !!!"
		else:
			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT UserName from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
		
			if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
				data = cursorObj.fetchone()
				if(data):
					error = "Thanks for filling form...!"
					return redirect(url_for('login1'))
			error = "Please try again..!!!" 
		
	return render_template('login2.html',form=form)'''

@app.route('/login2', methods=['GET', 'POST'])
def login2():
	form = MyForm()
	global username
	global password
	global locker
	error = ""

	if request.method=='POST':
		admin = request.form['admin']
		admin_pass = request.form['admin_pass']
		'''username = request.form['username']
		password = request.form['password']'''
		locker = request.form['locker']
		
		if admin != 'admin' or admin_pass != 'Admin@123':
			error = "Please try again !!!"
		else:
			error = "Thanks for filling form...!"
			return redirect(url_for('nominee'))
			'''con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT UserName from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
		
			if form.validate_on_submit(): # Use verify() method to see if ReCaptcha is filled out
				data = cursorObj.fetchone()
				if(data):
					error = "Thanks for filling form...!"
					return redirect(url_for('login1'))
			error = "Please try again..!!!" '''
		
	return render_template('login2.html',form=form,error=error)

@app.route('/nominee', methods=['GET', 'POST'])
def nominee():
	form = MyForm()
	global username
	global password
	global locker
	error = ""

	if request.method=='POST':
		'''admin = request.form['admin']
		admin_pass = request.form['admin_pass']'''
		username = request.form['username']
		password = request.form['password']
		locker = request.form['locker']
		
		'''if admin != 'admin' or admin_pass != 'Admin@123':
			error = "Please try again !!!"
		else:'''
		con = sqlite3.connect('banklocker.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT UserName from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
		
		#if form.validate_on_submit(): # Use verify() method to see if ReCaptcha is filled out
		data = cursorObj.fetchone()
		if(data):
			error = "Thanks for filling form...!"
			return redirect(url_for('nomineelogin'))
		error = "Please try again..!!!" 
		
	return render_template('nominee.html',form=form,error=error)


@app.route('/locker')
def locker():
	global lockers

	con = sqlite3.connect('banklocker.db')
	cursorObj = con.cursor()	
	cursorObj.execute(f"SELECT Time from Users WHERE UserName='{username}' AND Locker = '{locker}'")
	last_login=cursorObj.fetchone()
	print(type(last_login))

	#con = sqlite3.connect('banklocker.db')
	#cursorObj1 = con.cursor()

	d=datetime.now()
	login_time=d.strftime('%d/%m/%Y,%H:%M:%S')
	cursorObj.execute(f"UPDATE Users SET Time='{login_time}' WHERE UserName='{username}'")
	con.commit()
	return render_template('locker.html',locker=locker,last_login=last_login)



@app.route('/video_stream')
def video_stream():

	return Response(video_feed(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	
	global email
	error = ""

				
	if request.method=='POST':
			
		email = request.form['email']
		try:
			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT email, username, Password from Users WHERE email = '{email}'")	
			data = cursorObj.fetchone() 

			
			if(data[0] == email):
				receiver_email = email

				message = MIMEMultipart("alternative")
				message["Subject"] = "Forgot Password."
				message["From"] = sender_email
				message["To"] = receiver_email

				html = """\
							<html>
							<body>
								<p>Email : <strong>{receiver_email}</strong><br>
								Password : {password}<br>
								<a href="127.0.0.1:5000/login">Login</a>						
								</p>
							</body>
							</html>
						""".format(receiver_email=receiver_email,password=data[2])
				innermsg = MIMEText(html, "html")
				message.attach(innermsg)

				context = ssl.create_default_context()
				with smtplib.SMTP_SSL("mail.eternalgig.com", 465, context=context) as server:
					server.login(sender_email, sender_password)
					server.sendmail(sender_email, receiver_email, message.as_string())
					error = "Mail Sent to register email."
				

			con.commit()
			#return render_template('forgot.html',error=error)

		except TypeError:
			error = "User not Register....!!"
			#return redirect(url_for('forgot'))

	return render_template('forgot.html',error=error)


@app.route('/helpdesk', methods=['GET', 'POST'])
def helpdesk():
	
	global email
	global problem_category
	global problem_statement
	error = ""

	if request.method=='POST':
		
		email = request.form['email']		
		problem_category = request.form['problem_category']
		problem_statement = request.form['problem_statement']	
		admin_mail='rowdymaari0611@gmail.com'	

		
		try:
			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT email, UserName, Locker, Nominee from Users WHERE email = '{email}'")	
			data = cursorObj.fetchone() 

			
			if(data[0] == email):
				receiver_email = email
				#admin
				message = MIMEMultipart("alternative")
				message["Subject"] = "Help...!."
				message["From"] = sender_email
				message["To"] = sender_email

				html = """\
							<html>
							<body><h2><strong>{user_type} User Account.</strong></h2><br>
								<p>Username : <strong>{username}</strong><br>
								Email : <strong>{email}</strong><br>
								Locker ID : <strong>{locker}</strong><br><br><br>

								<strong>{problem_category} : </strong>
								{problem_statement}
								</p>						
							</body>
							</html>
						""".format(user_type=data[3],username=data[1],email=data[0],locker=data[2],problem_category=problem_category,problem_statement=problem_statement)
				innermsg = MIMEText(html, "html")
				message.attach(innermsg)

				context = ssl.create_default_context()
				with smtplib.SMTP_SSL("mail.eternalgig.com", 465, context=context) as server:
					server.login(sender_email, sender_password)
					server.sendmail(sender_email, sender_email, message.as_string())


				#user
				message = MIMEMultipart("alternative")
				message["Subject"] = "Help...!."
				message["From"] = sender_email
				message["To"] = receiver_email

				html = """\
							<html>
							<body><h3>Mail copy of your problem.</strong></h3><br>
							<h2><strong>{user_type} User Account.</strong></h2><br>
								<p>Username : <strong>{username}</strong><br>
								Email : <strong>{email}</strong><br>
								Locker ID : <strong>{locker}</strong><br><br><br>

								<strong>{problem_category} : </strong>
								{problem_statement}
								</p>						
							</body>
							</html>
						""".format(user_type=data[3],username=data[1],email=data[0],locker=data[2],problem_category=problem_category,problem_statement=problem_statement)
				innermsg = MIMEText(html, "html")
				message.attach(innermsg)

				with smtplib.SMTP_SSL("mail.eternalgig.com", 465, context=context) as server:
					server.login(sender_email, sender_password)
					server.sendmail(sender_email, receiver_email, message.as_string())
					
					error = "Mail Sent to helpdesk center."
		except TypeError:
					error = 'User Not Register, So we can not help you.'
     
	return render_template('helpdesk.html',error=error)

	
# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True, threaded=True)




























