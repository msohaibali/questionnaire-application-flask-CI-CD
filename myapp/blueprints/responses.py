# from os import name
from datetime import datetime
from myapp.model.model import User
from flask  import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from myapp.model.db_extension import db

questionare = Blueprint('questionare', __name__)

@questionare.route('/get_form_data')
def get_form_data():
    pass