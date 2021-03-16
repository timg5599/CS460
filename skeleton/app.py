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

@app.route("/createalbum", methods=['GET'])
def make_album():
    return render_template('createalbum.html')

@app.route("/createalbum", methods=['POST'])
def create_album():
    try:
        albumname = request.form.get('albumname')
    except:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('createalbum'))
    cursor = conn.cursor()
    isUnique = isAlbumUnique(albumname)
    if isUnique:
        print(cursor.execute("INSERT INTO Albums (album_name, user_id) VALUES ('{0}', '{1}')".format(albumname, getUserId())))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Album Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('create_album'))

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

@app.route("/Feed2/search", methods=['POST', 'GET'])
def search_photo():
    search = request.form.get('search_input')
    try:
        myID= getUserId()
        cursor = conn.cursor()
    except:
        print("couldn't find all tokens")
        return '''<H1>You need to login</H1>"'''

    else:
        return render_template('Feed2.html', photos=getSearchPhotos(getUserId(),search),photo_comment =getSearchComment(search), base64=base64)


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

def isAlbumUnique(albumname):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT album_name FROM Albums WHERE album_name = '{0}'".format(albumname)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

@app.route('/profile')
@flask_login.login_required
def protected():
        uid=getUserId()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',albums = getUsersAlbums(uid), photos=getUsersPhotos(uid), base64=base64)



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
        update_scorebyone()
        album = getAlbumId(request.form.get('album'))
        photo_data = imgfile.read()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES (%s, %s, %s, %s )''',
                       (photo_data, uid, caption, album))
        conn.commit()
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(uid), base64=base64 )
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')

def getAlbumId(albumname):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(albumname))
    return cursor.fetchall()

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT album_name, album_date, album_id FROM Albums WHERE user_id = '{0}'".format(uid))
    album_list = cursor.fetchall()
    album_ids = []
    for i in range(len(album_list)):
        album_ids.append(album_list[i][0])
        # album_ids.append([album_list[i][0], album_list[i][2]])
        
    return album_list

def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption, numLike FROM Pictures WHERE user_id = '{0}'".format(uid))
    picture_list = cursor.fetchall()
    new_tuple_with_comment = []
    for i in range(len(picture_list)):
        pid = picture_list[i][1]
        if(cursor.execute("select text,email from(SELECT comment.p_id,comment.u_id,comment.text,users.email FROM comment INNER JOIN users ON comment.u_id = users.user_id) as newcomment where p_id ={0}".format(pid))):
            comment = cursor.fetchall()
            temp = (picture_list[i][0],picture_list[i][1],picture_list[i][2],picture_list[i][3],comment)
            new_tuple_with_comment.append(temp)
        else:
            temp = (picture_list[i][0],picture_list[i][1], picture_list[i][2], picture_list[i][3])
            new_tuple_with_comment.append(temp)
        #(img,pictureid, caption,numlikes,comments (text,email))
    return new_tuple_with_comment # NOTE list of tuples, [(imgdata, pid), ...]

def getUserAlbumPhotos(uid, album):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption, numLike FROM Pictures WHERE user_id = '{0}' AND album_id = '{1}'".format(uid, album))
    picture_list = cursor.fetchall()
    new_tuple_with_comment = []
    for i in range(len(picture_list)):
        pid = picture_list[i][1]
        if(cursor.execute("select text,email from(SELECT comment.p_id,comment.u_id,comment.text,users.email FROM comment INNER JOIN users ON comment.u_id = users.user_id) as newcomment where p_id ={0}".format(pid))):
            comment = cursor.fetchall()
            temp = (picture_list[i][0],picture_list[i][1],picture_list[i][2],picture_list[i][3],comment)
            new_tuple_with_comment.append(temp)
        else:
            temp = (picture_list[i][0],picture_list[i][1], picture_list[i][2], picture_list[i][3])
            new_tuple_with_comment.append(temp)
        #(img,pictureid, caption,numlikes,comments (text,email))
    return new_tuple_with_comment # NOTE list of tuples, [(imgdata, pid), ...]


def getFriendPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption, numLike FROM Pictures WHERE user_id in (Select f_id as user_id from friends where u_id ={0});".format(uid))
    picture_list = cursor.fetchall()
    new_tuple_with_comment = []
    for i in range(len(picture_list)):
        pid = picture_list[i][1]
        if(cursor.execute("select text,email from(SELECT comment.p_id,comment.u_id,comment.text,users.email FROM comment INNER JOIN users ON comment.u_id = users.user_id) as newcomment where p_id ={0}".format(pid))):
            comment = cursor.fetchall()
            temp = (picture_list[i][0],picture_list[i][1],picture_list[i][2],picture_list[i][3],comment)
            new_tuple_with_comment.append(temp)
        else:
            temp = (picture_list[i][0],picture_list[i][1], picture_list[i][2], picture_list[i][3])
            new_tuple_with_comment.append(temp)
        #(img,pictureid, caption,numlikes,comments (text,email))
    return new_tuple_with_comment # NOTE list of tuples, [(imgdata, pid), ...]

def getSearchPhotos(uid,searchstr):
    cursor = conn.cursor()
    str= searchstr
    cursor.execute("Select * from (SELECT imgdata, picture_id, caption, numLike FROM Pictures WHERE user_id in (Select f_id as user_id from friends where u_id ='{0}'))as picture_list where caption like '%{1}%';".format(uid,str))
    picture_list = cursor.fetchall()
    new_tuple_with_comment = []
    for i in range(len(picture_list)):
        pid = picture_list[i][1]
        if(cursor.execute("select text,email from(SELECT comment.p_id,comment.u_id,comment.text,users.email FROM comment INNER JOIN users ON comment.u_id = users.user_id) as newcomment where p_id ={0}".format(pid))):
            comment = cursor.fetchall()
            temp = (picture_list[i][0],picture_list[i][1],picture_list[i][2],picture_list[i][3],comment)
            new_tuple_with_comment.append(temp)
        else:
            temp = (picture_list[i][0],picture_list[i][1], picture_list[i][2], picture_list[i][3])
            new_tuple_with_comment.append(temp)

    return new_tuple_with_comment # NOTE list of tuples, [(imgdata, pid), ...]

def getSearchComment(searchstr):
    cursor = conn.cursor()
    str= searchstr
    cursor.execute("select imgdata, picture_id, caption, numLike from pictures where picture_id in(select p_id as p_id from comment where text like '%{0}%')".format(str))
    picture_list = cursor.fetchall()
    new_tuple_with_comment = []
    for i in range(len(picture_list)):
        pid = picture_list[i][1]
        if(cursor.execute("select text,email from(SELECT comment.p_id,comment.u_id,comment.text,users.email FROM comment INNER JOIN users ON comment.u_id = users.user_id) as newcomment where p_id ={0}".format(pid))):
            comment = cursor.fetchall()
            temp = (picture_list[i][0],picture_list[i][1],picture_list[i][2],picture_list[i][3],comment)
            new_tuple_with_comment.append(temp)
        else:
            temp = (picture_list[i][0],picture_list[i][1], picture_list[i][2], picture_list[i][3])
            new_tuple_with_comment.append(temp)
        #(img,pictureid, caption,numlikes,comments (text,email))
    return new_tuple_with_comment # NOTE list of tuples, [(imgdata, pid), ...]

def update_scorebyone():
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET score = score + 1 WHERE user_id ='{0}'".format(getUserId()))
    conn.commit()

    
@app.route('/profile/album', methods=['POST'])
def show_album_photos():
    # WORKING HERE
    aid = request.form.get('album_id')
    uid=getUserId()
    return render_template('showalbumpictures.html', photos = getUserAlbumPhotos(uid, aid), base64=base64)


@app.route('/profile/like', methods=['POST'])
def like_photo():
    print("liked photo")
    pid= request.form.get('photo_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE pictures SET numLike = numLike + 1 WHERE picture_id ='{0}'".format(pid))
    conn.commit()
    return render_template('hello.html', name=flask_login.current_user.id,
                               photos=getUsersPhotos(getUserId()), base64=base64)
@app.route('/Feed2/like', methods=['POST'])
def like_photo_friend():
    print("liked photo")
    pid= request.form.get('photo_id')
    cursor = conn.cursor()
    cursor.execute("UPDATE pictures SET numLike = numLike + 1 WHERE picture_id ='{0}'".format(pid))
    conn.commit()
    return render_template('feed2.html', name=flask_login.current_user.id,
                               photos=getFriendPhotos(getUserId()), base64=base64)


@app.route('/profile/comment', methods=['POST'])
def comment_photo():
    pid= request.form.get('photo_id')
    text = request.form.get('comment')
    print(pid,text)
    cursor = conn.cursor()
    update_scorebyone()
    cursor.execute("INSERT INTO comment (u_id,p_id,text) VALUES ('{0}','{1}','{2}')".format(getUserId(),pid,text))
    conn.commit()
    return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotos(getUserId()), base64=base64)

@app.route('/Feed2/comment', methods=['POST'])
def comment_photo_friend():
    pid= request.form.get('photo_id')
    text = request.form.get('comment')
    update_scorebyone()
    print(pid,text)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comment (u_id,p_id,text) VALUES ('{0}','{1}','{2}')".format(getUserId(),pid,text))
    conn.commit()
    return render_template('Feed2.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getFriendPhotos(getUserId()), base64=base64)



# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')

@app.route("/Feed2", methods=['GET'])
def feed():
       photos = getFriendPhotos(getUserId())
       return render_template('Feed2.html', photos=photos, base64=base64)

@app.route("/LeaderBoard", methods=['GET'])
def get_ranking():
    cursor = conn.cursor()
    cursor.execute("select email,score from users order by score desc LIMIT 3")
    data = cursor.fetchall()
    return render_template('LeaderBoard.html', datas= data)




def getUserId():
    return getUserIdFromEmail(flask_login.current_user.id)

def getEmailwithID(uid):
    if cursor.execute("SELECT email  FROM Users WHERE  userid= '{0}'".format(uid)):
        return cursor.fetchone()[0]

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
