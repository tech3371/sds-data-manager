from sqlalchemy import MetaData

from sds_data_manager.lambda_code.SDSCode import indexer


def test_batch_job_event(test_engine, test_db_uri):
    # NOTE: batch event has more information than this but
    # only kept information critical for testing
    # and changed account number to fake number
    event = {}
    metadata = MetaData()
    metadata.reflect(bind=test_engine)
    for table_name in metadata.tables:
        print("table in test file ", table_name)

    print(test_db_uri())
    returned_value = indexer.lambda_handler(event, {})
    assert returned_value is None
