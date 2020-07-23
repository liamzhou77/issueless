from datetime import timedelta
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
SQLALCHEMY_DATABASE_URI = (
    os.environ.get('DATABASE_URL') or 'postgresql://liamzhou@localhost/issueless'
)
AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_SECRET_KEY')
LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
SQLALCHEMY_TRACK_MODIFICATIONS = False
REMEMBER_COOKIE_DURATION = timedelta(days=3, hours=1)
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
START_NGROK = os.environ.get('START_NGROK') is not None
S3_ACCESS_KEY = os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.environ.get('BUCKETEER_BUCKET_NAME')
