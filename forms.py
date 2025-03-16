from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class UpdateProfileForm(FlaskForm):

    username = StringField("Username", 
        validators=[DataRequired()], 
        render_kw={"class": "form-control", "placeholder": "Enter username"})

    email = StringField("Email", 
        validators=[DataRequired(), Email()], 
        render_kw={"class": "form-control", "placeholder": "Enter email address"})

class ProfileForm(FlaskForm):
    username = StringField("Username", 
        validators=[DataRequired()], 
        render_kw={"class": "form-control", "placeholder": "Enter username"})

    email = StringField("Email", 
        validators=[DataRequired(), Email()], 
        render_kw={"class": "form-control", "placeholder": "Enter email address"})




class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()], 
                        render_kw={"class": "form-control", "placeholder": "Enter email address"})
    
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)], 
                           render_kw={"class": "form-control", "placeholder": "Enter username"})
    
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)], 
                             render_kw={"class": "form-control", "placeholder": "Enter password"})
    
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')], 
                                     render_kw={"class": "form-control", "placeholder": "Confirm password"})
    
    submit = SubmitField("Create account", render_kw={"class": "btn btn-primary", "style": "width: 100%; margin: 10px auto;"})

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()], 
                        render_kw={"class": "form-control", "placeholder": "Enter email address"})
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")



class CreateArticleForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(message="Title is required"),
        Length(min=1, max=20)
    ])

    body = TextAreaField('Content', validators=[
        DataRequired(message="Article content is required"),
        Length(min=5,max=500)
    ])

    category_id = SelectField('Category', coerce=int, validators=[
        DataRequired(message="Please select a category")
    ])

    thumbnail = FileField('Thumbnail Image', validators=[])
    

    submit = SubmitField('Publish Article')



class CommentForm(FlaskForm):
    body = TextAreaField(
    "Say something about the article",
    validators=[DataRequired()],
    render_kw={"class": "form-control", "rows": 3, "placeholder": "Say something about the article"}
)
submit = SubmitField("Post Comment")