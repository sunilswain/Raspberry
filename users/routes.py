from flaskblog.models import User
from flask import render_template,url_for, flash , redirect, request, abort, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.users.utils import SavePicture, send_reset_email
from flaskblog.users.forms import( ResistrationForm , LogInForm, UpdateAccountForm,
                             RequestResetForm, ResetPasswordForm)

users = Blueprint('users', __name__)

@users.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            view_post = request.args.get('view_post')
            if view_post:
                return redirect(url_for('posts.post'))
            elif next_page:
                return redirect(url_for('users.account'))
            else:
                return redirect(url_for('main.home_page'))   
            # return redirect(url_for('posts.post')) if view_post else redirect(url_for('main.home_page'))
            # return redirect(url_for('users.account')) if next_page else redirect(url_for('main.home_page'))
        else:
            flash("Unsuccessful login , please check your email and password. " , "warning" )
    return render_template('log_in.html', title = "login" , form = form)

@users.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = ResistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user1 = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user1)
        db.session.commit()
        flash(f'hello {form.username.data} , your account has created . you can log in now .' , "success")
        return redirect(url_for('main.home_page'))
    return render_template('signUp.html', title = "signup" , form = form)


@users.route("/logout", methods = ["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('main.home_page'))


@users.route("/account", methods = ["GET", "POST"])
@login_required
def account():
    # return redirect(url_for('users.account'))
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = SavePicture(form.profile_picture.data,current_user.pfp)
            current_user.pfp = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated successfully','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_picture/'+  current_user.pfp )
    return render_template('account.html', title = 'account', image_file = image_file, form = form) 


@users.route("/reset_password", methods = ["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to your account with proper instructios. ','succes' )
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',title = 'request reset password ',  form = form)


@users.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_token():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This token is invalid or expired !' , 'warning')
        return redirect(url_for('users.reset_request'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f' your password has been updated successfully . you can log in now .' , "success")
        return redirect(url_for('main.home_page'))
    return render_template('reset_token.html',title = 'request reset password ',  form = form)
    
