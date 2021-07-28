import os, secrets
from PIL import Image
from flask import render_template,url_for, flash , redirect, request, abort
from flaskblog import app, db, bcrypt,mail
from flaskblog.forms import( ResistrationForm , LogInForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



@app.route("/")
@app.route("/home")
def home_page():
    page = request.args.get('page',1,type = int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page ,per_page = 7)
    return render_template('home.html',posts = posts)

@app.route("/about")
def about_page():

    return render_template('about.html')



@app.route("/login", methods = ["GET", "POST"])
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

@app.route("/register", methods = ["GET", "POST"])
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


@app.route("/logout", methods = ["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('main.home_page'))

def SavePicture(form_picture, prev_pfp):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    prev_pfp_path = os.path.join(app.root_path, 'static\profile_picture', prev_pfp)
    if prev_pfp != "default.png":
        os.remove(prev_pfp_path)
    picture_path = os.path.join(app.root_path, 'static\profile_picture', picture_fn)

    pfp_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(pfp_size)
    i.save(picture_path)


    return picture_fn

@app.route("/account", methods = ["GET", "POST"])
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


@app.route("/post/new", methods = ["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title = form.title.data , content = form.content.data ,bg = form.bg.data, author = current_user)
        db.session.add(post)
        db.session.commit()
        flash('your post has successfully posted.', 'success')
        return redirect(url_for('posts.new_post'))
    return render_template('create_post.html', title = 'new_post', form = form , legend ='create post')

@app.route("/post/<int:post_id>" )
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title = post.title, post = post ) 
 
@app.route("/post/<int:post_id>/update" , methods = ["GET","POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # post.bg = form.bg.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')
    
@app.route("/post/<int:post_id>/delete" , methods = ["POST"]) 
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted successfully !', 'success')
    return redirect(url_for('main.home_page'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type = int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author = user).\
            order_by(Post.date_posted.desc()).\
            paginate(page = page ,per_page = 7)
    return render_template('user_posts.html',posts = posts,user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Reset Password Request',
                    sender = 'Admin@bluberry.com' ,
                    recipients = [user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

    

@app.route("/reset_password", methods = ["GET", "POST"])
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


@app.route("/reset_password/<token>", methods = ["GET", "POST"])
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
    
