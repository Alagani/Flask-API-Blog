from flask import render_template, request,redirect, url_for, flash
from flask_login import LoginManager,login_user, login_required, logout_user, current_user
from slugify import slugify
from sqlalchemy import or_
import os
from flask_login import login_user
from werkzeug.security import check_password_hash
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from forms import *
from models import *

login_manager = LoginManager(app)
login_manager.login_view = "signin"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegisterForm()
    
    if form.validate_on_submit():
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_email:
            flash("Email is already registered. Try logging in.", "danger")
            return render_template("signup.html", form=form)

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("signin"))  
        except:
            db.session.rollback()

    return render_template("signup.html", form=form)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated: 
        return redirect(url_for("home"))  

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("signin.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('signin'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))