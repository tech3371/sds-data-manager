import pytest

from sds_data_manager.lambda_code.SDSCode.path_helper import FilenameParser


def test_date_checker():
    """Tests date inputs"""
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    file_parser = FilenameParser(filename)
    assert file_parser.check_date_input("20200101")
    assert not file_parser.check_date_input("2020-01-01")
    assert not file_parser.check_date_input("202301")


filename_and_expected_inputs = [
    ("imap_glows_l0_raw_20231010_20231011_v01-01.pkts", True, "Correct"),
    ("imap_hi-45_l0_raw_20231010_20231011_v01-06.pkts", True, "Correct"),
    ("imap_glows_l0_raw_20231010_20231011_v01-02.cdf", False, "Invalid file extension"),
    (
        "imap_glows_l1a_raw_20231010_20231011_v01-03.pkts",
        False,
        "Invalid file extension",
    ),
    ("imap_glows_l0__20231010_20231011_v01-04.pkts", False, "Empty descriptor"),
    ("imap_hi-45_l0_raw_20231010_20231011_v01.pkts", False, "Invalid version format"),
    ("imap_hi-45_l0_raw_20231010_20231011_v1-1.pkts", False, "Invalid version format"),
    ("imap_hi-45_l3_raw_20231010_20231011_v01-01.cdf", False, "Unsupported data level"),
]


@pytest.mark.parametrize(("filename", "expected", "msg"), filename_and_expected_inputs)
def test_filename_validator(filename, expected, msg):
    """Validate filenames"""
    assert FilenameParser(filename).validate_filename() == expected, msg


def test_upload_filepath():
    """Test response from upload path function"""
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
