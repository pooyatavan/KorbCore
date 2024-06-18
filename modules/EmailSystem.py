import re, random, smtplib

from modules.ConfigReader import config

recovery_codes = {}
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def email_server(email):
    code = str(random.sample(range(100000, 900000), 1))
    code = code.replace("[", "").replace("]", "")
    if recovery_codes:
        if code not in recovery_codes:
            recovery_codes[code] = {'email': f'{email}'}
            send_email(email, code)
        else:
            email_server(email)
    else:
        recovery_codes[code] = {'email': f'{email}'}
        send_email(email, code)

def send_email(email, code):
    email_content = f"کد جهت بازیابی کلمه عبور اکانت: {code}"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(config['email']['username'], config['email']['password'])
    server.sendmail(email, email, email_content)

def email_check(email):
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False