import boto3
from botocore.client import Config
import os
from dotenv import load_dotenv

load_dotenv()


class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=os.getenv("MINIO_ENDPOINT"),
            aws_access_key_id=os.getenv("MINIO_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("MINIO_SECRET_KEY"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self.bucket = os.getenv("MINIO_BUCKET")

    def upload_file(self, file_obj, key: str, content_type="application/octet-stream"):
        self.client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=self.bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type},
        )

    def get_file_url(self, key: str, expires_in: int = 3600, response_content_disposition: str | None = None) -> str:
        params = {"Bucket": self.bucket, "Key": key}

        if response_content_disposition:
            params["ResponseContentDisposition"] = response_content_disposition

        return self.client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires_in,
        )


s3_client = S3Client()
