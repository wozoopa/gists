import json
import urllib
import boto3
import sys
import logging

from cStringIO import StringIO

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
mystdout = StringIO()
region = "us-east-1"


client = boto3.client('datapipeline', region)

def lambda_handler(event, context):
    try:
        response = client.activate_pipeline(
            pipelineId='df-092384092340jkdhfg8'
            )
        return response
    except Exception as e:
        print(e)
        raise e
