# Define the application directory
import os

# Statement for enabling the development environment
DEBUG = True
# SERVER_NAME = "127.0.0.1"
# SERVER_PORT = 8080


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
# SQLALCHEMY_DATABASE_URI = 'mysql://root:1234561@127.0.0.1/testing'

DB_ENGINE = "mysql"
SCHEMA_NAME = "metadata_gathering"
DB_PORT = 3306
DB_HOST = "127.0.0.1"
DB_USERNAME = "stream_user"
DB_PASSWORD = "Bdl.12345"

NEO_HOST = "127.0.0.1"
NEO_PORT = 7474


SQLALCHEMY_DATABASE_URI = (
    "{DB_ENGINE}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
        DB_ENGINE=DB_ENGINE,
        DB_USERNAME=DB_USERNAME,
        DB_PASSWORD=DB_PASSWORD,
        DB_HOST=DB_HOST,
        DB_NAME=SCHEMA_NAME,
    )
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "whatyoudoinghereitsamystery"

# # Tables Names
# USERS_TABLE = "users"
# POSTS_TABLE = "posts"

EMAIL = "sohaib@gmail.com"
PASSWORD = "1234"
