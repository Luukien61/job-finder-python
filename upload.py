import boto3
from botocore.exceptions import NoCredentialsError

# Cấu hình AWS
AWS_ACCESS_KEY = 'AKIA6GBMGIC66CPQBL6P'
AWS_SECRET_KEY = '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'
AWS_REGION = 'ap-southeast-1'
BUCKET_NAME = 'jobfinder-kienluu'


def upload_file_to_s3(file_path, bucket_name, object_name=None):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    # Nếu object_name không được cung cấp, đặt tên file giống như tên file gốc
    if object_name is None:
        object_name = file_path.split("/")[-1]

    try:
        # Tải file lên S3
        s3_client.upload_file(file_path, bucket_name, object_name, ExtraArgs={'ACL': 'public-read'})

        # Lấy URL của file trên S3
        url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{object_name}"
        return url

    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
