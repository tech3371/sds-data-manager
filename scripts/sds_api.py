import requests
import json
import os
import datetime

# THESE MUST BE RESET EVERY TIME FOR NOW
COGNITO_CLIENT_ID = "4rtf569eq2brgk3sq8ek4uqc91"
UPLOAD_API_URL = "https://vo54qpw7fy4uarorbxnplilgae0hhwos.lambda-url.us-west-2.on.aws/"
DOWNLOAD_API_URL = 'https://i5y2mfaoh3capmulqehouzcjya0zwedr.lambda-url.us-west-2.on.aws/' 
QUERY_API_URL = 'https://stkjssplyeb5deqgn25wiaix2y0icvzg.lambda-url.us-west-2.on.aws/'

USER_TOKEN = None
LOGIN_TIME = None

def _set_user_token(t):
    global USER_TOKEN
    global LOGIN_TIME

    LOGIN_TIME = datetime.datetime.now()
    USER_TOKEN = t


def _get_user_token():
    global USER_TOKEN
    global LOGIN_TIME
    if LOGIN_TIME is None:
        print("New login needed.  Login is valid for 60 minutes.")
    elif (datetime.datetime.now() - LOGIN_TIME).total_seconds() >= 3600:
        print("Login expired.  Please log in again.")
    else:
        return USER_TOKEN

    t = get_sdc_token()

    return t


def get_sdc_token(user_name=None, password=None):
    '''
    This function authenticates the user.  An access token is automatically stored in the USER_TOKEN
    variable in this file, and functions will attempt to find a valid user token in that variable.

    :param user_name: User's SDC username
    :param password: User's SDC password

    :return: A string that also gets stored in the USER_TOKEN variable in this file.  You don't need this string unless
             you plan on making your own API calls, using functions outside of this file.
    '''
    global COGNITO_CLIENT_ID
    if user_name is None:
        user_name = input("Username:")
    if password is None:
        import getpass
        password = getpass.getpass("Password for " + user_name + ":")

    authentication_url = "https://cognito-idp.us-west-2.amazonaws.com/"
    authentication_headers = {'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
                              'Content-Type': 'application/x-amz-json-1.1'}
    data = json.dumps({"ClientId": COGNITO_CLIENT_ID, "AuthFlow": "USER_PASSWORD_AUTH",
                       "AuthParameters": {"USERNAME": user_name, "PASSWORD": password}})

    # Attempt to grab the SDC token.
    try:
        token_response = requests.post(authentication_url, data=data, headers=authentication_headers)
        t = token_response.json()['AuthenticationResult']['AccessToken']
    except KeyError:
        print("Invalid username and/or password.  Please try again.  ")
        return

    _set_user_token(t)

    return t    

def _execute_api(url, **kwargs):
    token = _get_user_token()
    headers = {"Authorization": token}
    query_parameters = []
    for kw in kwargs:
        query_parameters.append(kw + "=" + str(kwargs[kw]))
    query_parameters = '&'.join(query_parameters)
    url_with_parameters = url + "?" + query_parameters
    print(url_with_parameters)
    try:
        response = requests.get(url_with_parameters, headers=headers)
    except Exception as e:
        print(f"Could not finish query due to error {str(e)}")
        return
    return response

def download(filename, download_dir=''):
    '''
    This function is used to download files from the SDS.
    
    :param filename: The full S3 URI to download
    :param download_dir: The directory on the local machine to download the file to.  

    :return: None, but downloads the file to the specified download directory
    '''
    global DOWNLOAD_API_URL
    download_url = _execute_api(DOWNLOAD_API_URL, s3_uri=filename)

    if (download_url.status_code == 400):
        print("Not a valid S3 URI.  Example input: s3://bucket/path/file.ext")
        return
    elif (download_url.status_code == 404):
        print("No files were found matching the given URI.")
        return

    file_name_and_path = os.path.join(download_dir, filename[5:])
    download_dir = os.path.dirname(file_name_and_path)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    with open(file_name_and_path, 'wb') as file:
        print(f"Downloading {file_name_and_path}")
        file_location = requests.get(download_url.json()["download_url"])
        file.write(file_location.content)
    
    return file_location

def query(**kwargs):
    '''
    This function is used to query files from the SDS.  
    There are no required arguments, the search strings will depend on the mission

    :return: This returns JSON with all information about the files.
    '''
    global QUERY_API_URL
    response = _execute_api(QUERY_API_URL, **kwargs)
    return response.json()

def upload(file_location, file_name, **kwargs):
    '''
    This function is used to upload files to the SDS.  
    
    :param file_location: The path to the file on the local machine to upload to the SDS.  
    :param file_name: The name of the file you'd like to upload
    :param kwargs: Any additional key word arguments passed into this function are stored as tags on the SDS.

    :return: This returns a requests response object.  If the upload was successful, it'll be code 200.  
    '''
    global UPLOAD_API_URL
    response = _execute_api(UPLOAD_API_URL, filename=file_name, **kwargs)
    
    if response.status_code != 200:
        print(f"Could not generate an upload URL with the following error: {response.text}")
        return

    with open(file_location, 'rb') as object_file:
        object_text = object_file.read()
    response = requests.put(response.json(), data=object_text)
    return response

if __name__ == "__main__":
    #x = upload(file_location='helloworld.txt', file_name='imap_l0_sci_mag_2024_2.pkts', testing='true')
    #print(x)
    #x = query(instrument='mag')
    #print(x)
    x = download("s3://sds-data-harter-asdfasdf/imap/l0/imap_l0_sci_mag_2024_2.pkts")
    print(x)