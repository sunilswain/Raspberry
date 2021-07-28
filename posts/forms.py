from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired 

class PostForm(FlaskForm):
    title = StringField('title' , validators = [DataRequired()])
    content = TextAreaField('content', validators = [DataRequired()])
    submit = SubmitField('Post')
    update = SubmitField('Update')
    delete = SubmitField('Delete')