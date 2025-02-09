import functools
from random import randint

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from magicmirror.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if (user_id is None):
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if (g.user is None):
            return redirect(url_for('auth.login'))
        
        return(view(**kwargs))
    return(wrapped_view)


def get_new_user_id(users):
    taken_user_ids = []
    for user in users:
        taken_user_ids.append(user['id'])
    while True:
        new_user_id = randint(0, 999999999)
        print(new_user_id)
        if (new_user_id not in taken_user_ids):
            break
    return(new_user_id)


def get_new_device_id():
    db = get_db()
    devices = db.execute(
        'SELECT *'
        ' FROM Device'
    ).fetchall()
    taken_device_ids = []
    for device in devices:
        taken_device_ids.append(device['id'])
    while True:
        new_device_id = randint(0, 999999999)
        if (new_device_id not in taken_device_ids):
            break
    return new_device_id



@bp.route('/register', methods = ['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if (not username):
            error = 'Username is required!'
        if (not password):
            error = 'Password is required!'

        if (error is None):
            try:
                users = db.execute(
                    'SELECT * FROM User'
                ).fetchall()
                new_user_id = get_new_user_id(users)
                db.execute(
                    "INSERT INTO User (id, username, password) VALUES (?, ?, ?)",
                    (new_user_id, username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
    return(render_template('auth/register.html'))



@bp.route('/login', methods = ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        if (user is None):
           error = 'Incorrect username!'
        elif not (check_password_hash(user['password'], password)):
            error = 'Incorrect password!'

        if (error is None):
           session.clear()
           session['user_id'] = user['id']
           return redirect(url_for('index'))

        flash(error)
    return(render_template('auth/login.html'))



@bp.route('/device_login', methods = ('POST',))
def device_login():
    content = request.get_json()
    if (not content):
        return("Bad Request: No JSON in POST.", 400)
    
    try:
        username = content['username']
    except:
        return("Bad Request: element 'username' not present in JSON.", 400)
    
    try:
        password = content['password']
    except:
        return("Bad Request: element 'password' not present in JSON.", 400)
    
    try:
        device_name = content['device_name']
    except:
        return("400: Bad Request, missing 'device_name' element in JSON.", 400)

    try:
        device_auth = content['device_pubkey']
    except:
        return("400: Bad Request, missing 'device_pubkey' element in JSON.", 400)
   


    db = get_db()     
    user = db.execute(
        'SELECT * FROM User WHERE username = ?',
        (username,)
    ).fetchone()

    if (user is None):
        return("Bad Request: Incorrect username!", 400)
    elif not (check_password_hash(user['password'], password)):
        return("Bad Request: Incorrect password!", 400)
    else:
        new_device_id = get_new_device_id()
        db.execute(
            'INSERT INTO Device (id, name, owner, owner_name, pubkey)'
            ' VALUES (?, ?, ?, ?, ?)',
            (new_device_id, device_name, user['id'], user['username'], device_auth) 
        )
        db.execute(
            'INSERT INTO DeviceUserAssociation (user_id, device_id)'
            ' VALUES (?, ?)',
            (user['id'], new_device_id)
        )
        db.commit()
        return jsonify(status="Success", device_id=new_device_id)




@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
