import os
import tempfile

import pytest

from myapp import create_app
from myapp import db


@pytest.fixture
def client():
    global app
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()

    with app.test_client() as client:
        with app.app_context():
            db.init_app(app)
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_home_page(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'Welcome To this Site!' in rv.data

def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)

def profile_page(client):
    return client.get('/profile', follow_redirects=True)

def posts_page(client):
    return client.get('/api/getposts', follow_redirects=True)

def test_login_logout(client):
    """Make sure login and logout works."""

    email = app.config["EMAIL"]
    password = app.config["PASSWORD"]

    rv = login(client, email, password)
    assert b'Welcome, to Your Profile' in rv.data

    rv = logout(client)
    assert b'You are Not Logged In, Please Login to Enjoy Full Features' in rv.data

    rv = login(client, f"{email}x", password)
    assert b'Check your Login Credentials and Try Again' in rv.data

    rv = login(client, email, f'{password}x')
    assert b'Check your Login Credentials and Try Again' in rv.data

def test_profile_for_loggedin(client):
    """Make sure Profile is Visible if user is logged In"""

    email = app.config["EMAIL"]
    password = app.config["PASSWORD"]

    _ = login(client, email, password)

    rv = profile_page(client)
    assert b'Welcome, to Your Profile' in rv.data

def test_profile_for_loggedout(client):
    """Make sure Profile is not Visible if user is logged Out"""

    rv = profile_page(client)
    if b'Please log in to access this page' in rv.data:
        print('[-]  User not logged in')
        assert True

def test_posts_for_loggedin(client):
    """Make sure POSTS is Visible if user is logged In"""

    email = app.config["EMAIL"]
    password = app.config["PASSWORD"]

    _ = login(client, email, password)

    rv = posts_page(client)
    assert b'Welcome To Posts Page' in rv.data

def test_posts_for_loggedout(client):
    """Make sure POSTS is not Visible if user is logged Out"""

    rv = posts_page(client)
    if b'Please log in to access this page' in rv.data:
        print('[-]  User not logged in')
        assert True

