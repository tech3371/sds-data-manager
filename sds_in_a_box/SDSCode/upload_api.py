import json
import os
import requests
import time
import boto3
from jose import jwk, jwt
from jose.utils import base64url_decode


def _load_allowed_filenames():
    # Rather than storing the configuration locally, we should store the configuration somewhere where things can be changed on the fly.  
    # For example, a dynamodb table or a section in opensearch
    current_dir = os.path.dirname(__file__)
    config_file = os.path.join(current_dir, "config.json")
    
    with open(config_file) as f:
        data = json.load(f)
    return data

def _check_for_matching_filetype(pattern, filename):
    
    split_filename = filename.replace("_", ".").split(".")

    if len(split_filename) != len(pattern):
        return None
    
    i = 0
    file_dictionary = {}
    for field in pattern:
        if pattern[field] == '*':
            file_dictionary[field] = split_filename[i]
        elif pattern[field] == split_filename[i]:
            file_dictionary[field] = split_filename[i]
        else:
            return None
        i += 1
    
    return file_dictionary

def _generate_signed_upload_url(filename, tags={}):
    
    filetypes = _load_allowed_filenames()
    for filetype in filetypes:
        path_to_upload_file = filetype['path']
        metadata = _check_for_matching_filetype(filetype['pattern'], filename)
        if metadata is not None:
            break
        
    if metadata is None:
        logger.info(f"Found no matching file types to index this file against.")
        return None
    
    bucket_name = os.environ["S3_BUCKET"]
    url = boto3.client('s3').generate_presigned_url(ClientMethod='put_object', 
                                                    Params={'Bucket': bucket_name[5:], 
                                                    'Key': path_to_upload_file+filename, 
                                                    'Metadata': tags}, 
                                                    ExpiresIn=3600)
    
    return url

def lambda_handler(event, context):
    
    if 'filename' not in event['queryStringParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Please specify a filename to upload")
        }
        
    filename = event['queryStringParameters']['filename']
    url = _generate_signed_upload_url(filename, tags=event['queryStringParameters'])
    
    if url is None:
        return {
            'statusCode': 400,
            'body': json.dumps("A pre-signed URL could not be generated. Please ensure that the file name matches mission file naming conventions.")
        }
    
        
    return {
        'statusCode': 200,
        'body': json.dumps(url)
    }
