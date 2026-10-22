from django.conf import settings
from rest_framework import serializers
from annai_candles_be.file_upload_to_aws import put_file_to_s3
import uuid


def build_file_url(instance, folder):
    if not instance or not instance.file_name or not instance.file_ext:
        return None

    path = f"{settings.IMAGE_BASE_URL}/{settings.COMPANY_NAME}/{folder}"

    if instance.id:
        path += f"/{instance.id}"

    return f"{path}/{instance.file_name}.{instance.file_ext}"




def upload_file_to_s3(file_obj, folder, entity_id):
    if file_obj is None or file_obj == "null" or file_obj == "":
        raise serializers.ValidationError("A valid file is required.")

    file_name = uuid.uuid4()
    ext = file_obj.name.split(".")[-1].lower().strip()
    if not ext:
        raise serializers.ValidationError("File extension is required.")
    
    s3_key = (
        f"{settings.COMPANY_NAME}/{folder}/{entity_id}/{file_name}.{ext}"
    )
    
    if not put_file_to_s3(file_obj, s3_key, public=False):
        raise serializers.ValidationError("Failed to upload file to storage.")

    return file_name, ext