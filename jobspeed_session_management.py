import sqlite3
from flask import Flask, session, request, make_response
from flask_bcrypt import Bcrypt
import os
import datetime
from time import gmtime, strftime
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

jobspeed_api = Flask(__name__)

bcrypt = Bcrypt(jobspeed_api)

jobspeed_api.secret_key = os.urandom(24)
jobspeed_api.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=9, minutes=30)

blacklisted_users = {}

@jobspeed_api.route('/', methods=['POST'])
def start_session():
    # 2 variables will be POST a user and a password
    # this code may change as request.data.whatever may not be the correct syntax
    user = request.form.get('username')
    if user in blacklisted_users:
        if (time.time() - blacklisted_users[user]) > 2700:
            blacklisted_users.pop(user, None)
        else:
            blacklist_cookie = make_response("Setting Cookie")
            blacklist_cookie.set_cookie("blacklisted", "blacklisted", max_age=60*45)
            return blacklist_cookie
    else:
        print("user not in black list")
        pass
    try:
        session.pop(user)
    except:
        pass

    passwurd_attempt = request.form.get('passwurd_attempt')

    if request.method == 'POST':
        conn = sqlite3.connect('jobspeed_ids.db')
        c = conn.cursor()
        c.execute("""SELECT jobspeedpass, paid FROM CustomerIdTable WHERE jobspeeduser=(?)""", (user,))
        data = c.fetchone()[0]
        conn.close()
        salted_pw = data.encode('utf-8')

        if bcrypt.check_password_hash(salted_pw, passwurd_attempt) == True:

            conn = sqlite3.connect('jobspeed_ids.db')
            c = conn.cursor()
            c.execute("""SELECT paid FROM CustomerIdTable WHERE jobspeeduser=(?)""", (user,))
            paid = c.fetchone()[0]
            conn.close()
            print(paid)

            if paid == 1:
                # they user has paid and access is granted
                session_id = os.urandom(12)
                session[user] = session_id #session id is same length as secret key (which signs the cookie)
                print(session)
                print(session[user])
                # write the session details to sqlite
                conn_session = sqlite3.connect('session_data.db')  # Change this to a REDIS database later
                c_session = conn_session.cursor()
                with conn_session:
                    c_session.execute("DELETE FROM SessionIdTable WHERE user=(?)", (user,))
                with conn_session:
                    c_session.execute("""INSERT INTO SessionIdTable(user, sessionid) VALUES(?, ?)""",
                               (user, session_id))
                    print("database updated")
                return "something"
            elif paid == 0:
                # access is denied because they haven't paid the fee this month
                return
        else:
            print("nope")
            # either the username or pass word was incorrect
            return
        return
    return

@jobspeed_api.route('/is_session_active/', methods=['POST'])
def is_session_active():

    user = request.form.get('user_active_sesh') #hopefully grab the user

    conn_session = sqlite3.connect('session_data.db')  # Change this to a REDIS database later
    c_session = conn_session.cursor()
    c_session.execute("""SELECT sessionid FROM SessionIdTable WHERE user=(?)""", (user,))
    check_sessionid = c_session.fetchone()[0]
    conn_session.close()

    if session.get(user) == check_sessionid:
        print(check_sessionid)
        print("session remains the same")
        print(session.get(user))
        return "something"
        # session is valid IT WAS YOU WHO WAS LOGGED IN LAST!
        # continue
    else:
        try:
            conn = sqlite3.connect('jobspeed_ids.db')
            c = conn.cursor()
            c.execute("""SELECT companyname FROM CustomerIdTable WHERE jobspeeduser=(?)""", (user,))
            data = c.fetchone()[0]

            session.pop(user)

            current_secs_since_epoch = time.time()
            blacklisted_users[user] = current_secs_since_epoch

            logout_cookie = make_response("Setting Cookie")
            logout_cookie.set_cookie("session already in use", "logout", max_age=60*5)
            gmail_user = GMAIL_USER
            gmail_pass = GMAIL_PASS

            msg = MIMEMultipart()
            msg['From'] = formataddr(('JobSpeed Alert', GMAIL_USER))  
            msg['To'] = GMAIL_USER
            msg['Subject'] = 'ALERT: ' + user + ': Conflicting login'
            attempt_time = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
            body = 'User: ' + user + '\nCompany: ' + data + '\n\n A conflicting login in was attempted at: ' + attempt_time
            msg.attach(MIMEText(body, 'plain'))
            text = msg.as_string()
            conn.close()

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(gmail_user, gmail_pass)

                server.sendmail(gmail_user, GMAIL_USER, text)
                server.quit()
                print("Email Sent!")
            except:
                print("Something went wrong...")

            return logout_cookie
        except:
            print("already popped")
        print(session.get(user))
        print("popped")
        return "popped"
        # somebody (or you has logged in before the session was due to expire in 9.5 hours)
        # log them out send them to loggin screen
        # The session is active please wait 5 minutes
        # since you've logged in somebody else has logged in BECAUSE this will only get fired AFTER a successful login
        # somebody else is using your credentials

'''
def create_session_id_table():
    c_session.execute(""""CREATE TABLE IF NOT EXISTS SessionIdTable(user TEXT, sessionid TEXT)""")
    # loggedin 1 for TRUE 0 for FALSE

def create_customer_id_table():
    c.execute(""""CREATE TABLE IF NOT EXISTS CustomerIdTable(companyname TEXT, jobspeeduser TEXT, jobspeedpass TEXT,
     paid INTEGER)""")
    # paid is a boolean but boolean is not a seperate storage class in sqlite3 so I will use 0 as FASLE and 1 as TRUE
'''
def new_data_entry(company_name, user, passwurd, paid):
    # Add password hashing here
    hashed_pw = bcrypt.generate_password_hash(passwurd).decode('utf-8')
    conn = sqlite3.connect('jobspeed_ids.db')
    c = conn.cursor()
    with conn:
        c.execute("""INSERT INTO CustomerIdTable(companyname, jobspeeduser, jobspeedpass, paid) VALUES(?, ?, ?, ?)""",
                  (company_name, user, hashed_pw, paid))

if __name__ == '__main__':
    jobspeed_api.run(debug=False)
