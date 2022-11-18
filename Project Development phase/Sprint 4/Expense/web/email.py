
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

def sendMail(subject,message,to_email):
    try:
        sg = sendgrid.SendGridAPIClient(api_key='apikey')
        from_email = Email("rohit@gmail.com")  
        content = Content("text/plain", message)
        mail = Mail(from_email, to_email, subject, content)
        mail_json = mail.get()

        response = sg.client.mail.send.post(request_body=mail_json)
        # print(response.status_code)
        # print(response.headers)
        return response.status_code
    
    except:
        return 404
