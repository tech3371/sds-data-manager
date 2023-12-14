"""This stores database configuration such as database URI"""
import json
import os

import boto3


def get_db_uri():
    """Create DB URI from secret manager.
    Returns:
        str: DB URI
    """
    secret_name = os.environ["SECRET_NAME"]
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    secret_string = client.get_secret_value(SecretId=secret_name)["SecretString"]
    secret = json.loads(secret_string)
    return f'postgresql://{secret["username"]}:{secret["password"]}@{secret["host"]}:{secret["port"]}/{secret["dbname"]}'


db_uri = get_db_uri()
