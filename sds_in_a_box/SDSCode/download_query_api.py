import boto3
import os


def http_response(header_type='text/html', status_code=200, body='Success'):
    """customize http response.

    Args:
        header_type (str, optional): [description]. Defaults to 'text/html'.
        status_code (int, optional): [description]. Defaults to 200.
        body (str, optional): [description]. Defaults to 'Success'.

    Returns:
        [json]: API response
    """
    return  {
        'headers': {
            'Content-Type': header_type,
        },
        'statusCode': status_code,
        'body': body
    }

def lambda_handler(event, context):
    """This lambda handler checks if this file exists or not. If file doesn't exist, it
    gives back an error. Otherwise, it returns pre-signed s3 url that user can use to donwload
    data from s3.

    Args:
        event (dict): input to lambda
        context : This is not used.
    """

    if event['queryStringParameters'] is None or 'filepath' not in event['queryStringParameters'] or 'bucket' not in event['queryStringParameters']:
        response_body = f'''Missing input parameter. It requires bucket and filepath.\n
                        bucket: S3 bucket name\n
                        filepath: full file path with filname. Eg. dir1/subdir/filename.pkts
                        '''
        return http_response(status_code=421, body=response_body)

    bucket = event['queryStringParameters']['bucket']
    filepath = event['queryStringParameters']['filepath']
    s3_client = boto3.client('s3')

    # check if object exists
    try:
        s3_client.head_object(Bucket=bucket, Key=filepath)
    except Exception as e:
        return http_response(status_code=404, body='File not found in S3.')

    pre_signed_url = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': filepath},
                                                    ExpiresIn=os.environ['URL_EXPIRE'])
    return pre_signed_url

event = {
    "version": "2.0",
    "routeKey": "$default",
    "rawPath": "/",
    "rawQueryString": "filename=test_tenzin.txt&event=sky",
    "headers": {
        "sec-fetch-mode": "navigate",
        "x-amzn-tls-version": "TLSv1.2",
        "sec-fetch-site": "none",
        "accept-language": "en-US,en;q=0.9",
        "x-forwarded-proto": "https",
        "x-forwarded-port": "443",
        "x-forwarded-for": "128.138.131.13",
        "sec-fetch-user": "?1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "x-amzn-tls-cipher-suite": "ECDHE-RSA-AES128-GCM-SHA256",
        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?0",
        "x-amzn-trace-id": "Root=1-63d87ec7-13d194014f4c840b670a3fa8",
        "sec-ch-ua-platform": "\"macOS\"",
        "host": "i4mmi7nwd4bvqzxtfuwivnadou0ynlnc.lambda-url.us-west-2.on.aws",
        "upgrade-insecure-requests": "1",
        "accept-encoding": "gzip, deflate, br",
        "sec-fetch-dest": "document",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    },
    "queryStringParameters": {
        "bucket": "delete-later-tenzin",
        "filepath": "sds_in_a_box/SDSCode/science_block_20221116_163611Z_idle.bin"
    },
    "requestContext": {
        "accountId": "anonymous",
        "apiId": "i4mmi7nwd4bvqzxtfuwivnadou0ynlnc",
        "domainName": "i4mmi7nwd4bvqzxtfuwivnadou0ynlnc.lambda-url.us-west-2.on.aws",
        "domainPrefix": "i4mmi7nwd4bvqzxtfuwivnadou0ynlnc",
        "http": {
            "method": "GET",
            "path": "/",
            "protocol": "HTTP/1.1",
            "sourceIp": "128.138.131.13",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        },
        "requestId": "41090832-b4f2-4f8c-b465-6b92b45f6d5b",
        "routeKey": "$default",
        "stage": "$default",
        "time": "31/Jan/2023:02:36:55 +0000",
        "timeEpoch": 1675132615290
    },
    "isBase64Encoded": False
}

response = lambda_handler(event, None)
print(response)