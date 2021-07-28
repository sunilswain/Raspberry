import os, secrets
from PIL import Image
from flaskblog import  mail
from flask_mail import Message
from flask import url_for, current_app

def SavePicture(form_picture, prev_pfp):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    prev_pfp_path = os.path.join(current_app.root_path, 'static\profile_picture', prev_pfp)
    if prev_pfp != "default.png":
        os.remove(prev_pfp_path)
    picture_path = os.path.join(current_app.root_path, 'static\profile_picture', picture_fn)

    pfp_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(pfp_size)
    i.save(picture_path)


    return picture_fn



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

    