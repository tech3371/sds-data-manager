import json
import urllib.parse
import boto3
import logging 

s3 = boto3.client('s3')

def load_allowed_filenames():
    # Rather than storing the configuration locally, we should store the configuration somewhere where things can be changed on the fly.  
    # For example, a dynamodb table or a section in opensearch
    with open("/workspace/SDS-in-a-box/sds_in_a_box/lambdas/file-indexer/config.json") as f:
        data = json.load(f)
    return data

def check_for_matching_filetype(pattern, filename):
    split_filename = filename.replace("_", ".").split(".")

    if len(split_filename) != len(pattern):
        return None
    
    i = 0
    file_dictionary = {}
    for field in pattern:
        
    
    return None

def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, indent=2))

    # Retrieve a list of allowed file types
    filetypes = load_allowed_filenames()
    logger.info("Allowed file types: " + filetypes)

    # We're only expecting one record, but for some reason the Records are a list object
    for record in event['Records']:
        logger.info(f'Record Received: {record}')

        bucket = record['s3']['bucket']['name']

        filename = record['s3']['object']['key']

        logger.info(f"Attempting to insert {filename} into database")

        for filetype in filetypes:
            metadata = check_for_matching_filetype(filetype['pattern'], filename)

            if metadata is not None:
                break
        
        return metadata


    
