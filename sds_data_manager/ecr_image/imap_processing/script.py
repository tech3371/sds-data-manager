#!/usr/bin/env python3
import os

from imap_processing.swe import decom_swe


def handler(event, context):
    # This is a dummpy code that runs in batch job
    instrument = os.environ.get("INSTRUMENT", "SWE")
    if instrument == "SWE":
        data_file = "/usr/local/lib/python3.11/site-packages/imap_processing/swe/tests/science_block_20221116_163611Z_idle.bin"
        decom_data = decom_swe.decom_packets(data_file)
        print(decom_data[0].header)
    else:
        print(f"{instrument} not supported yet")

    return "Hello from Lambda!"
