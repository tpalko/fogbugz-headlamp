# Statement for enabling the development environment
DEBUG = True

ALLOW_REGISTRATION = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

FOGBUGZ_URL="https://sample.fogbugz.com"
FOGBUGZ_ACCOUNT_NAME="user@sample.com"
FOGBUGZ_PASSWORD="secret"

# - comma-delimited names and billing rates (names as found in fogbugz)
BILLING_NAMES=""
BILLING_RATES=""

user="sample"
password="secret"
host="127.0.0.1"
port=5432
database="sample_dbname"

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://%s:%s@%s:%s/%s?client_encoding=utf8' %(user, password, host, port, database)

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
SECRET_KEY = "secret"

DATE_FORMAT = "%B %d, %Y"
BABEL_DATE_FORMAT = 'MMMM d, YYYY'
DATETIME_FORMAT = "%A %B %d, %Y %H:%M"

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'America/New_York'