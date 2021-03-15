######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

# for image uploading
import os, base64

from sqlalchemy import null

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'qwer1234'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email from Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password,first_name,last_name,hometown,gender) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(email, password,firstname,lastname,hometown,gender)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))


@app.route("/search_complete", methods=['POST'])
def follow_user():
    try:
        friendId = request.form.get('user_id')
        print(friendId)
        myId = getUserId()
        print(myId)
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return render_template('search_complete.html', supress='True')
    cursor = conn.cursor()
    print(cursor.execute("INSERT INTO Friends (u_id, f_id) VALUES ('{0}', '{1}')".format(myId, friendId)))
    conn.commit()
    return render_template('search_complete.html', supress='True')


@app.route("/friendList", methods=['POST'])
def unfollow_user():
    try:
        friendId = request.form.get('f_id')
        print(friendId)
        myId = getUserId()
        print(myId)
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return render_template('friendList.html', supress='True')
    cursor = conn.cursor()
    print(cursor.execute("Delete from Friends Where u_id = '{0}' and f_id ='{1}' ".format(myId, friendId)))
    conn.commit()
    return render_template('friendList.html', supress='True')


@app.route("/hello", methods=['POST', 'GET'])
def search_users():
    search = request.form.get('search')
    try:
        myID= getUserId()
        cursor = conn.cursor()
    except:
        print("couldn't find all tokens")
        return '''<H1>You need to login</H1>"'''

    if cursor.execute("SELECT user_id,email FROM users where email LIKE '%{0}%' and user_id <> '{1}' and user_id not in (Select f_id as user_id from (SELECT friends.u_id,friends.f_id,users.email FROM friends INNER JOIN users ON friends.f_id = users.user_id) as friendList where u_id = '{1}')" .format(search,myID)):
        data_list = cursor.fetchall()
        print(data_list[0])
        return render_template('search_complete.html', datas=data_list)
    else:
        return '''<H1>"No Search Result"</H1><a href='/'>Home</a>'''


@app.route("/friendList", methods=['GET'])
def list_friends():
    myId = getUserId()
    cursor = conn.cursor()
    if cursor.execute("Select f_id,email from (SELECT friends.u_id,friends.f_id,users.email FROM friends INNER JOIN users ON friends.f_id = users.user_id) as friendList where u_id = '{0}' ;".format(myId)):
        data_list = cursor.fetchall()
        if cursor.execute("SELECT user_id,email FROM users where user_id <> '{0}' and user_id not in (Select f_id as user_id from (SELECT friends.u_id,friends.f_id,users.email FROM friends INNER JOIN users ON friends.f_id = users.user_id) as friendList where u_id ='{0}') order by rand() Limit 5".format(myId)):
            recommand_list = cursor.fetchall()
        return render_template('friendList.html', datas=data_list, friend_recommandation=recommand_list)
    else:
        return '''<H1>"you have no friends Yet"</H1><a href='/'>Home</a>'''





def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def getUserScoreByEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT score  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
    uid=getUserId()
    return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid), base64=base64)


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        photo_data = imgfile.read()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''',
                       (photo_data, uid, caption))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid), base64=base64)
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption,numLike FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

@app.route('/profile', methods=['POST'])
def like_photo():
    pid= request.form.get('photo_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE pictures SET numLike = numLike + 1 WHERE picture_id ='{0}'".format(pid))
    return render_template('hello.html', name=flask_login.current_user.id,
                               photos=getUsersPhotos(getUserId()), base64=base64)

@app.route('/profile', methods=['POST'])
def comment_photo():
    pid= request.form.get('photo_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE pictures SET numLike = numLike + 1 WHERE picture_id ='{0}'".format(pid))
    return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(getUserId()), base64=base64)
# end photo uploading code


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


def getUserId():
    return getUserIdFromEmail(flask_login.current_user.id)



if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
