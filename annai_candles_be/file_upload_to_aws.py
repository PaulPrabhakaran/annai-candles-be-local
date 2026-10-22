import logging
import botocore
from django.conf import settings
import os
import boto3

from annai_candles_be.common import get_s3_session

logger = logging.getLogger("annai_candles_be")


def put_image_to_s3(file_obj, folder_name):
    """
    Put the file to s3
    :param file_obj:
    :return:
    """

    print("FILE SIZE ===== ", file_obj.size)
    print("Content Type ===== ", file_obj.content_type)

    s3_filename = f"{folder_name}"
    session = get_s3_session()
    s3 = session.resource("s3")
    try:
        s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(
            Key="%s" % s3_filename,
            Body=file_obj.read(),
            ContentDisposition="attachment; filename=%s" % s3_filename,
            ContentType="%s" % file_obj.content_type,
        )
        return True
    except botocore.exceptions.ClientError as e:
        print("ERR 1 : ", str(e))
    except Exception as e:
        print("ERR 2 : ", str(e))
    return False


def put_file_to_s3(file_obj, folder_name, public=True):
    """
    Put the guide file to s3
    :param t_uuid:
    :param file_name:
    :param file_obj:
    :param public:
    :return:
    """
    s3_filename = f"{folder_name}"

    print("S3 FILE Name = ", s3_filename)

    logger.info("Starting uploading file to s3")
    session = get_s3_session()
    s3 = session.resource("s3")
    put_param = {
        "Key": "%s" % s3_filename,
        "Body": file_obj.read(),
        "ContentDisposition": "attachment; filename=%s" % s3_filename,
        "ContentType": "%s" % file_obj.content_type,
    }

    if public:
        put_param["ACL"] = "public-read"
    else:
        put_param["ACL"] = "private"

    try:
        s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(**put_param)
        logger.info("Completed uploading file to s3")
        return True
    except botocore.exceptions.ClientError as e:
        logger.info("Unable to upload file: {} to s3".format(file_obj.name))
        logger.error("Original exception occurred {}".format(str(e)))
    except Exception as e:
        logger.info("Unable to upload file: {} to s3".format(file_obj.name))
        logger.error("Original exception occurred {}".format(str(e)))
    return False
