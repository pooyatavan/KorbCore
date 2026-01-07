import smtplib

from ConfigReader import config

def send_email(email, code):
    email_content = f"کد جهت بازیابی کلمه عبور اکانت: {code}"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    server.sendmail(email, email, email_content)

