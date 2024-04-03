from flask import Flask
from flask_mail import Mail, Message



# Configure your app for the email server
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rowdymaari0611@gmail.com'
app.config['MAIL_PASSWORD'] = 'Khushal@8805'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# Initialize the Mail object
mail = Mail(app)

@app.route("/email")
def index():
    msg = Message('Hello', sender = 'rowdymaari0611@gmail.com', recipients = ['khushal.chaudhari.2001@gmail.com'])
    msg.body = "This is the email body"
    mail.send(msg)
    
    return "Sent"

if _name_ == '_main_':
    app.run(debug = True)