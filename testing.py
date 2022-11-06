from sds_in_a_box.SDSCode import indexer

# This is a pretend new file payload, like we just received "imap_l0_instrument_date_version.fits" from the bucket "IMAP-Data-Bucket"
sample_payload = {
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "IMAP-Data-Bucket"
        },
        "object": {
          "key": "imap_l0_instrument_date_version.fits",
          "size": 1305107
        }
      }
    }
  ]
}

indexer.lambda_handler(sample_payload, "This does literally nothing")