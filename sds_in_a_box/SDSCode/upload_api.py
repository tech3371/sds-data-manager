import json
import os
import requests
import time
import boto3
from jose import jwk, jwt
from jose.utils import base64url_decode

def _verify_cognito_token(token):
    
    '''
     This function verifies that a cognito token that we've received is:
         - Actually from the expected userpool
         - Not expired
         - From the correct cognito client ID
    '''

    region = 'us-west-2'
    userpool_id = os.environ["COGNITO_USERPOOL_ID"]
    app_client_id = os.environ["COGNITO_APP_ID"]
    keys_url = f'https://cognito-idp.{region}.amazonaws.com/{userpool_id}/.well-known/jwks.json'
    response = requests.get(keys_url)
    keys = (response.json())['keys']
    
    headers=jwt.get_unverified_headers(token)
    kid=headers['kid']
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['client_id'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims

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
    
    verified_token = False
    try:
        token=event["headers"]["authorization"]
        verified_token = _verify_cognito_token(token)
    except Exception as e:
        logger.info(f"Authentication error: {e}")


    if not verified_token:
        logger.info("Supplied token could not be verified")
        return {
                'statusCode': 400,
                'body': json.dumps("Supplied token could not be verified")
            }

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
