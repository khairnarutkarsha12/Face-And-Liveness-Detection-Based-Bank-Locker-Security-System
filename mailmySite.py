# import the necessary packages
from xmlrpc.client import boolean
from flask import Flask, render_template, redirect, url_for, request, session, Response, flash
#from flask import *
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from password_strength import PasswordPolicy
from password_strength import PasswordStats
from datetime import datetime
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



##########################################################################################################################
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

		receiver_email = sender_email
		try:
			con = sqlite3.connect('banklocker.db')
			cursorObj = con.cursor()
			cursorObj.execute(f"SELECT email, UserName, Locker, Nominee from Users WHERE email = '{email}'")	
			data = cursorObj.fetchone() 

			
			if(data[0] == email):
				receiver_email = email
				message = MIMEMultipart("alternative")
				message["Subject"] = "Help...!."
				message["From"] = sender_email
				message["To"] = receiver_email

				html = """\
							<html>
							<body><h2><strong>{user_type}User Account.</strong></h2><br>
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
					server.sendmail(sender_email, receiver_email, message.as_string())

				with smtplib.SMTP_SSL("mail.eternalgig.com", 465, context=context) as server:
					server.login(sender_email, sender_password)
					server.sendmail(sender_email, email, message.as_string())
					
					error = "Mail Sent to helpdesk center."
		except TypeError:
					error = 'User Not Register, So we can not help you.'
     
	return render_template('helpdesk.html',error=error)
###########################################################################################################################
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




























