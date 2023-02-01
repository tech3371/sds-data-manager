import requests


def download_file(filename_and_path, download_link):
    """This allows user to download file from S3 using pre-signed URL generated
    by the download query API.

    Args:
        filename_and_path (str): exact path with filename where user want to store.
            Eg. dir/subdir/filename.ext
        download_link (str): pre-signed URL from S3
    """
    # Get file content using requests
    response = requests.get(download_link, stream=True)

    # save/write file content to file on local machine
    if response.status_code == 200:
        with open(filename_and_path, 'wb') as file:
            print(f"Downloading {filename_and_path}")
            file.write(response.content)
    else:
        print("Failed to download file")