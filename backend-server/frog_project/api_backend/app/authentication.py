from flask import Blueprint, render_template, redirect, url_for, request, make_response
from .classes import User, Frog, Image
from flask_login import login_required, login_user, logout_user, current_user
from . import db
from .common import make_json_response


authentication = Blueprint('authentication', __name__)


@authentication.route('/login', methods=['GET', 'POST'])
def login_post():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return make_json_response(False, msg="login failed", code="unauthorized")

        login_user(user.id, remember=remember)
        return make_json_response(msg="login successful")
    else:
        response = '''
        <!doctype html><title>Frog</title><h1>Login</h1>
        <form method=post enctype=multipart/form-data><input type=text name=username>
        <input type=password name=password><input type=submit value=Upload></form>
        '''
    response = make_response(response)
    return response
    

@authentication.route('/new-user', methods=['POST'])
@login_required
def new_user_post():
    if current_user.username != "admin":
        return make_json_response(False, msg="User is not admin", code="forbidden")
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if user:
        return make_json_response(False, msg="User already exists", code="bad request")
    new_user = User(username=username)
    new_user.set_password(password=password)
    db.session.add(new_user)
    db.session.commit()
    return make_json_response(msg="Successfully created user")


@authentication.route('/new-user', methods=['GET'])
def new_user_get():
    admin_password = request.args.get('admin_password')
    username = request.args.get('username')
    password = request.args.get('password')


@authentication.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return make_json_response(msg="Successfully logged out")


