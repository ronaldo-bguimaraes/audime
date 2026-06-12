import os

import boto3

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

R2_ENDPOINT = os.environ["R2_ENDPOINT"]
R2_STORAGE_BUCKET = os.environ["R2_STORAGE_BUCKET"]

R2_ACCESS_KEY_ID = os.environ["R2_ACCESS_KEY_ID"]
R2_SECRET_ACCESS_KEY = os.environ["R2_SECRET_ACCESS_KEY"]


def get_s3_client():
    return boto3.client(
        service_name="s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto"
    )


def upload_file(local_path: str, key: str) -> None:
    client = get_s3_client()
    client.upload_file(local_path, R2_STORAGE_BUCKET, key)


def download_file(key: str, local_path: str) -> None:
    client = get_s3_client()
    client.download_file(R2_STORAGE_BUCKET, key, local_path)


def list_objects(prefix: str = "") -> list[str]:
    client = get_s3_client()
    keys: list[str] = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=R2_STORAGE_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys


def head_object(key: str) -> dict:
    client = get_s3_client()
    return client.head_object(Bucket=R2_STORAGE_BUCKET, Key=key)


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": R2_STORAGE_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )


if __name__ == "__main__":
    lista = list_objects("raw")
    print(lista)
