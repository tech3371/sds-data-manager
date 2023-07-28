#!/usr/bin/env python3

from imap_processing.swe import decom_swe


def handler(event, context):
    # This is a dummpy code that runs in batch job
    instrument = event.get("instrument", "SWE")
    if instrument == "SWE":
        pip_path = "/var/lang/lib/python3.11/site-packages"
        data_file = "science_block_20221116_163611Z_idle.bin"
        data_file = f"{pip_path}/imap_processing/swe/tests/{data_file}"
        decom_data = decom_swe.decom_packets(data_file)
        print(decom_data[0].header)
        return {"status": "SUCCEEDED"}
    else:
        print(f"{instrument} not supported yet")
        return {"status": "FAILED"}
