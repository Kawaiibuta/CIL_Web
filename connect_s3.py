# `import boto3` is importing the boto3 library in Python. Boto3 is the Amazon Web Services (AWS) SDK
# for Python, which allows Python developers to interact with various AWS services programmatically.
# By importing boto3, you can use its functions and classes to work with AWS services such as S3, EC2,
# DynamoDB, and more in your Python code.
# `import boto3` is a Python statement that imports the `boto3` library, which is the Amazon Web
# Services (AWS) SDK for Python. This library allows Python developers to interact with various AWS
# services programmatically.
import boto3
from botocore.exceptions import ClientError
import logging
import os
import json
from botocore.config import Config
from dotenv import load_dotenv
bucket_name = 'pycil.com'
load_dotenv()  # take environment variables from .env.

my_config = Config(
    region_name = 'ap-southeast-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

client = boto3.client(
    's3', 
    aws_access_key_id = os.getenv("ACCESS_KEY_ID"), 
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"), 
    config = my_config)

async def check_folder(key):
    result =[]
    response = client.list_objects_v2(Bucket=bucket_name,Delimiter="/", Prefix=key)
    sub_folder = response.get('CommonPrefixes')
    if sub_folder:
        for x in sub_folder:
            result.append(x.get("Prefix"))
    else:
        result.append(key)
    return result 
async def count_image(key):
    response = client.list_objects_v2(Bucket=bucket_name, Delimiter='/', Prefix=key)
    count = 0
    for x in response['Contents'][1:]:
        print(x)
        if x['Key'].split(".")[-1] == "jpg" or x['Key'].split(".")[-1] == "png":
            count += 1
    return count