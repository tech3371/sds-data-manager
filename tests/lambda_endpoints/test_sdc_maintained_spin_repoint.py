"""Test the SDC maintained SPIN repointing lambda."""

import os
from unittest.mock import patch

import pandas as pd
import pytest

from sds_data_manager.lambda_code.SDSCode.spice import (
    sdc_maintained_spin_repoint_handler,
)


@pytest.fixture(autouse=True)
def setup_s3(s3_client):
    """Populate the mocked s3 client with a bucket and a file.

    Each test below will use this fixture by default.
    """
    bucket_name = os.getenv("S3_BUCKET")
    s3_client.create_bucket(
        Bucket=bucket_name,
    )
    result = s3_client.list_buckets()
    assert len(result["Buckets"]) == 1
    assert result["Buckets"][0]["Name"] == bucket_name

    # patch the mocked client into the upload_api module
    # These have to be patched in because they were imported
    # prior to test discovery and would have the default values (None)
    with (
        patch.object(sdc_maintained_spin_repoint_handler, "S3_CLIENT", s3_client),
        patch.object(sdc_maintained_spin_repoint_handler, "S3_BUCKET", bucket_name),
    ):
        yield s3_client


def test_sdc_spin(s3_client):
    """Test the SDC maintained SPIN repointing lambda."""
    event = {
        "detail-type": "Object Created",
        "source": "aws.s3",
        "account": "449431850278",
        "region": "us-west-2",
        "detail": {
            "version": "0",
            "bucket": {"name": "sds-data-449431850278"},
            "object": {
                "key": "spice/spin/imap_2025_122_2025_122_01.spin.csv",
            },
        },
    }
    # Upload the test SPIN files
    # Write test data to pandas dataframe
    test_data = {
        "spin_number": [211, 212, 213],
        "spin_start_sec": [483843389, 483843399, 483843419],
        "spin_start_subsec": [0, 0, 0],
        "spin_period_sec": [15, 15, 15],
        "spin_period_valid": [1, 1, 1],
        "spin_phas_valid": [1, 1, 1],
        "spin_period_source": [0, 0, 0],
        "thruster_firing": [0, 0, 0],
    }
    test_data = pd.DataFrame(test_data)
    test_data.to_csv("imap_2025_122_2025_122_01.spin.csv", index=False)
    # Upload the test SPIN file to S3
    s3_client.upload_file(
        "imap_2025_122_2025_122_01.spin.csv",
        os.getenv("S3_BUCKET"),
        "spice/spin/imap_2025_122_2025_122_01.spin.csv",
    )
    response = sdc_maintained_spin_repoint_handler.lambda_handler(event, None)
    print(response)
