from django.core.management.base import BaseCommand, CommandError
import boto3
from botocore.exceptions import ClientError
import os

class Command(BaseCommand):
    help = 'Tests Amazon S3'

    def handle(self, *args, **options):
        fileName = os.path.abspath(os.getcwd()) + '/sample.mp3'
        s3Client = boto3.client('s3')
        try:
            response = s3Client.upload_file(fileName, 'unroutine-sequences', 'sample.mp3', ExtraArgs={'ACL': 'public-read'})
        except ClientError as e:
            print(e)

        print('finished')
