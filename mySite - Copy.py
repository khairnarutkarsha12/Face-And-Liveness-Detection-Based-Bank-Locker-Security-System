# import the necessary packages
from utils import *
from xmlrpc.client import boolean
from flask import Flask, render_template, redirect, url_for, request, session, Response, flash
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from password_strength import PasswordPolicy
from password_strength import PasswordStats
from datetime import datetime
from werkzeug.utils import secure_filename
import cv2

import pandas as pd
from playsound import playsound
import sqlite3


username=''
password=''
email=''
locker=''
login_time=''
max_attempt = 4

server_mail = 'mail.example.com'
port = 465
sender_email = 'bankadmin@example.com'
sender_password = '1234567890'

app = Flask(__name__)

#password_strength
policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 2 uppercase letters
    numbers=1,  # need min. 2 digits
    strength=0.10 # need a password that scores at least 0.5 with its entropy bits
)

@app.route('/', methods=['GET', 'POST'])
def input():
	
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
	
	
		if request.form['username'] != 'admin' or request.form['password'] != 'Admin@123':
			error = 'Please try again.'
		else:
			return redirect(url_for('home'))

	return render_template('input.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	
    
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
			

		return redirect(url_for('register1'))
		
	return render_template('register.html', message=message,error=error)

@app.route('/register1', methods=['GET', 'POST'])
def register1():
	global username
	global password
	global locker
	global email
	global nominee
	global login_time
	
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

		data = cursorObj.fetchone()       # Match database

		if(data and data[3]=='Active' and data[2]!=max_attempt):  # only if the data is matched and user is not blocked
			error = "Thanks for filling form...!"
			if(data[1].lower() == "nominee"):
				return redirect(url_for('login2'))
			else:
				return redirect(url_for('login1'))
		
		
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
							return redirect(url_for('locker'))
						else:

							error = 'Unknown Face Detected Plz Try again..!!'					
							current_count = current_count+1

							cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
							con.commit()
					except sqlite3.Error:
						error = 'database is lock, please restart your server'

			else:
				error = 'No Live Face Found'			
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
							return redirect(url_for('locker'))
						else:

							error = 'Unknown Face Detected Plz Try again..!!'					
							current_count = current_count+1

							cursorObj.execute(f"UPDATE Users SET Counter='{current_count}' WHERE UserName='{username}'")
							con.commit()
					except sqlite3.Error:
						error = 'database is lock, please restart your server'

			else:
				error = 'No Live Face Found'			
				current_count = current_count+1
		except IndexError:
			error = 'face not match' 
		
	return render_template('nomineelogin.html',username=username,password= password,locker=locker,error=error)



@app.route('/login2', methods=['GET', 'POST'])
def login2():
	
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
		
	return render_template('login2.html',error=error)

@app.route('/nominee', methods=['GET', 'POST'])
def nominee():
	
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
		cursorObj.execute(f"SELECT UserName from Users WHERE UserName = '{username}' AND Password = '{password}' AND Locker = {locker}")
		
		data = cursorObj.fetchone()
		if(data):
			error = "Thanks for filling form...!"
			return redirect(url_for('nomineelogin'))
		error = "Please try again..!!!" 
		
	return render_template('nominee.html',error=error)


@app.route('/locker')
def locker():
	global lockers

	con = sqlite3.connect('banklocker.db')
	cursorObj = con.cursor()	
	cursorObj.execute(f"SELECT Time from Users WHERE UserName='{username}' AND Locker = '{locker}'")
	last_login=cursorObj.fetchone()
	print(type(last_login))


	d=datetime.now()
	login_time=d.strftime('%d/%m/%Y,%H:%M:%S')
	cursorObj.execute(f"UPDATE Users SET Time='{login_time}' WHERE UserName='{username}'")
	con.commit()
	return render_template('locker.html',locker=locker,last_login=last_login)



@app.route('/video_stream')
def video_stream():

	return Response(video_feed(),mimetype='multipart/x-mixed-replace; boundary=frame')


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




























