from __future__ import print_function

import boto3

import os
import sys

from PIL import Image
import PIL.Image
# from resizeimage import resizeimage

BASE_WIDTH = 250
BASE_HEIGHT = 250
s3_client = boto3.client('s3')

def process_image_percent(width, height):
    # origin image width and height greater then base width or height
    if width < BASE_WIDTH or height < BASE_HEIGHT:
        return [width, height]

    # calculate image width and height percent
    if width > height:
        width_percent = BASE_WIDTH / float(width)
        resize_height = int((float(height) * float(width_percent)))
        return [BASE_WIDTH, resize_height]
    else:
        height_percent = BASE_HEIGHT / float(height)
        resize_width = int((float(width) * float(height_percent)))
        return [resize_width, BASE_HEIGHT]


def image_thumbnail(image_path, resized_path):

    image = Image.open(image_path)    
    resize_img = process_image_percent(image.size[0], image.size[1])

    thumbnail = image.resize((resize_img[0], resize_img[1]), PIL.Image.ANTIALIAS)
    thumbnail.save(resized_path, image.format)


def handler(event, context):
    for record in event['Records']:
        event_action = record['eventName']
        method = event_action.split(':')[1]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        file_name = os.path.basename(key)
        if not file_name.lower().endswith(('png', 'jpg', 'jpeg')):
            print('Filetype not valid for thumbnail')
            return 'Filetype not valid for thumbnail'

        download_path = '/tmp/{}'.format(file_name)
        upload_path = '/tmp/resized-{}'.format(file_name)

        if method=='Put' or method=='CompleteMultipartUpload':
            print('put thumbnail to s3 bucket')
            # download img to tmp folder
            s3_client.download_file(bucket, key, download_path)

            # save thumbnail img to upload_path
            image_thumbnail(download_path, upload_path)
            s3_client.upload_file(upload_path, '{bucket_name}-thumbnail'.format(bucket_name=bucket), key)
            return 'put thumbnail successfully'

        elif method=='Delete':
            print('delete thumbnail from s3 bucket')
            s3_client.delete_object(Bucket='{bucket_name}-thumbnail'.format(bucket_name=bucket), Key=key)
            return 'delete thumbnail successfully'

        else:
            return 'receive not match method, nothing to do'
