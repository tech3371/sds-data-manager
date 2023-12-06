import pytest

from sds_data_manager.lambda_code.SDSCode.path_helper import FilenameParser


def test_date_checker():
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    file_parser = FilenameParser(filename)
    assert file_parser.check_date_input("20200101")
    assert file_parser.check_date_input("2020-01-01") is False
    assert file_parser.check_date_input("202301") is False
    # NOTE: the date is correct but not in the format YYYYMMDD
    assert file_parser.check_date_input("2023105") is False


def test_filename_validator():
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    assert FilenameParser(filename).validate_filename() is True

    filename = "imap_hi-45_l0_raw_20231010_20231011_v01-06.pkts"
    assert FilenameParser(filename).validate_filename() is True

    # wrong extension for data level
    filename = "imap_glows_l0_raw_20231010_20231011_v01-02.cdf"
    assert FilenameParser(filename).validate_filename() is False
    filename = "imap_glows_l1a_raw_20231010_20231011_v01-03.pkts"
    assert FilenameParser(filename).validate_filename() is False

    # missing descriptor
    filename = "imap_glows_l0__20231010_20231011_v01-04.pkts"
    assert FilenameParser(filename).validate_filename() is False

    # missing enddate and it will raise
    filename = "imap_glows_l0_raw_20231010_v01-05.pkts"
    with pytest.raises(
        ValueError, match="not enough values to unpack"
    ) as not_enough_value:
        FilenameParser(filename).validate_filename()
    assert "not enough values to unpack (expected 7, got 6)" in str(
        not_enough_value.value
    )

    # version format is wrong
    filename = "imap_hi-45_l0_raw_20231010_20231011_v01.pkts"
    assert FilenameParser(filename).validate_filename() is False
    filename = "imap_hi-45_l0_raw_20231010_20231011_v1-1.pkts"
    assert FilenameParser(filename).validate_filename() is False

    # data level is not supported
    filename = "imap_hi-45_l3_raw_20231010_20231011_v01-01.cdf"
    assert FilenameParser(filename).validate_filename() is False


def test_upload_filepath():
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    file_parser = FilenameParser(filename)
    expected_path = f"imap/glows/l0/2023/10/{filename}"
    assert file_parser.upload_filepath()["statusCode"] == 200
    assert file_parser.upload_filepath()["body"] == expected_path

    # Gets defaul message
    filename = "imap_glows__raw_20231010_20231011_v01-01.pkts"
    file_parser = FilenameParser(filename)
    expected_msg = (
        "Invalid filename. Filename convention is "
        "<mission>_<instrument>_<datalevel>_<descriptor>_"
        "<startdate>_<enddate>_<version>.<extension>"
    )
    assert file_parser.upload_filepath()["statusCode"] == 400
    assert file_parser.upload_filepath()["body"] == expected_msg

    #  Gets custom message
    filename = "imap_glows_l0_raw_2023101_20231011_v01-01.pkts"
    file_parser = FilenameParser(filename)
    expected_msg = "Invalid start date format. Please use YYYYMMDD format."
    assert file_parser.upload_filepath()["statusCode"] == 400
    assert file_parser.upload_filepath()["body"] == expected_msg
