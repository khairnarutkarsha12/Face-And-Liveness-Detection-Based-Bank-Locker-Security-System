from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'AC8871b03b60198fe4351c909997c0e23a'
auth_token = '8743ba8257d00aa1ab7bd6c7a7f1b2c1'
client = Client(account_sid, auth_token)

def sendSMS(custom_body,username,locker_number):
    message = client.messages.create(
                        body=custom_body+'\nUsername: '+username+'\nLocker Number: '+locker_number,
                        from_='+19403146877',
                        to='+918975179845'
                    )
    print(message.sid)