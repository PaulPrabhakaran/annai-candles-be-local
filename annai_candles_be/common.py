from boto3 import Session
from django.conf import settings
import requests


custom_error_message = "Something Went Wrong"
permission_denied_message = "You Don't Have Permission"

session = requests.Session()

# default headers
session.headers = {"Content-Type": "application/json", "accept": "*/*"}


def get_s3_session():
    """
    Get s3 session
    :return:
    """
    session = Session(aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY)
    return session


def get_s3_client():
    """
    Get s3 client
    :return:
    """
    session = get_s3_session()
    client = session.client("s3")
    return client


def is_empty_or_whitespace(s):
    return not s.strip()
