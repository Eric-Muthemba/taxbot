import boto3
import os

AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_REGION_NAME=os.getenv('AWS_REGION_NAME')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')

client = boto3.client('textract',
                      region_name=AWS_REGION_NAME,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def extract_text_from_image(image_path):

    with open(image_path, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)

    response = client.detect_document_text(Document={'Bytes': bytes_test})
    return response["Blocks"][1]["Text"]



