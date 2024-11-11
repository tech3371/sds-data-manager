"""Define lambda to support the spin table API."""

import json


def lambda_handler(event, context):
    """TODO: write this docstring."""
    print(event)
    # TODO: extend this lambda code once we finish creating
    # spin table schema
    return {"statusCode": 200, "body": json.dumps("Hello from Spin Table Lambda!")}
