# Statement for enabling the development environment
DEBUG = True
# SERVER_NAME = "127.0.0.1"
# SERVER_PORT = 8080

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# SQLALCHEMY_DATABASE_URI = 'mysql://root:1234561@127.0.0.1/testing'
SQLALCHEMY_DATABASE_URI = 'mysql://stream_user:bdl12345@127.0.0.1/metadata_gathering'
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "whatyoudoinghereitsamystery"

# # Tables Names
# USERS_TABLE = "users"
# POSTS_TABLE = "posts"

EMAIL="sohaib@gmail.com"
PASSWORD="1234"