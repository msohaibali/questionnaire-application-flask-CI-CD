# from os import name
from datetime import datetime
from myapp.model.model import User
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from myapp.model.db_extension import db

auth = Blueprint("auth", __name__)


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/signup")
def signup():
    return render_template("signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home_page"))


@auth.route("/signup", methods=["POST"])
def signup_post():
    username = request.form.get("username").lower()
    password = request.form.get("password")
    created_at = datetime.now()

    # Incodicates user already exists in database
    user = User.query.filter_by(username=username).first()

    # Redirect to SignUp Page if user already exists
    if user:
        flash("User Already Exists with this Username")
        return redirect(url_for("auth.signup"))

    new_user = User(
        username=username,
        password=generate_password_hash(password, method="sha256"),
        created_at=created_at,
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("auth.login"))


@auth.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username").lower()
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash("Check your Login Credentials and Try Again")
        return redirect(url_for("auth.login"))

    # User has right credentials to login
    login_user(user, remember=remember)
    return redirect(url_for("main.get_profile"))
