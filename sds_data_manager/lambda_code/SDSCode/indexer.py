# Standard
import json
import logging
import os
import sys

# Installed
import boto3

# from .database.database import engine
from sqlalchemy import create_engine

# Local

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

s3 = boto3.client("s3")


def get_db_uri():
    """Create DB URI from secret manager.

    Returns
    --------
        str : DB URI
    """
    secret_name = os.environ["SECRET_NAME"]
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager")
    secret_string = client.get_secret_value(SecretId=secret_name)["SecretString"]
    db_config = json.loads(secret_string)
    return f'postgresql://{db_config["username"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["dbname"]}'


def lambda_handler(event, context, db_session=None):
    # TODO:
    print("lambda db uri", get_db_uri())

    if db_session is None:
        engine = create_engine(get_db_uri(), echo=True)
        print("engine", engine)
    # metadata = MetaData()
    # metadata.reflect(bind=engine)
    # print('tables from lambda ', metadata.tables)
    if db_session is not None:
        print(type(db_session))
        session = (
            db_session()
        )  # Create a session object from the scoped_session factory

        # Now, get the engine from the session's bind attribute
        engine = session.bind

    # You can now use engine with inspect or other operations
    from sqlalchemy import inspect

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(table_names)

    # Close the session when you're done
    session.close()

    # Add data to the corresponding instrument database
    # with Session(engine) as session:
    #     session.add(data)
    #     session.commit()
