import boto3
import os
import shutil

def lambda_handler(event, context):
    # Retrieve the S3 bucket and key from the event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    
    
    # Set the download path in the /tmp directory
    download_path = '/tmp/' + os.path.basename(s3_key)
    
    # Create an S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Download the file from S3
        s3_client.download_file(s3_bucket, s3_key, download_path)
        print(f"File downloaded: {download_path}")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
    
    # Move the file to the /mnt/efs directory
    destination_path = '/mnt/data/' + os.path.basename(s3_key)
    try:
        shutil.move(download_path, destination_path)
        print(f"File moved to: {destination_path}")
    except Exception as e:
        print(f"Error moving file: {str(e)}")

    print("After : ", os.listdir("/mnt/data"))
    
    # Add more logic here as needed
    
    return {
        'statusCode': 200,
        'body': 'File downloaded and moved successfully'
    }