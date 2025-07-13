import boto3
import os

from botocore.client import Config
from dotenv import load_dotenv
from fastapi import HTTPException, status
from io import BytesIO


load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    region_name=os.getenv("REGION_NAME"),
    config=Config(signature_version="s3v4"),
)

BUCKET_NAME = os.getenv("BUCKET_NAME")


def upload_to_s3(file_content: bytes, filename: str, content_type="video/mp4"):
    try:
        s3.upload_fileobj(
            Fileobj=BytesIO(file_content),
            Bucket=BUCKET_NAME,
            Key=filename,
            ExtraArgs={"ContentType": content_type},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file to S3: {e}",
        )
    return f"s3://{BUCKET_NAME}/{filename}" if BUCKET_NAME else None


def stream_from_s3(filename: str, byte_range: str):
    try:
        return s3.get_object(Bucket=BUCKET_NAME, Key=filename, Range=byte_range)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error streaming file from S3: {e}",
        )
