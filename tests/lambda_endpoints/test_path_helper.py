import pytest

from sds_data_manager.lambda_code.SDSCode.path_helper import (
    VALID_DATALEVELS,
    InvalidScienceFileError,
    ScienceFilepathManager,
)


def test_date_checker():
    """Tests date inputs"""
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    file_parser = ScienceFilepathManager(filename)
    assert file_parser.check_date_input("20200101")
    assert not file_parser.check_date_input("2020-01-01")
    assert not file_parser.check_date_input("202301")


filename_and_expected_inputs = [
    (
        "imap_glows_l0_raw_20231010_20231011_v01-02.cdf",
        False,
        (
            "Invalid extension. Extension should be pkts for data level l0 "
            "and cdf for data level higher than l0"
        ),
    ),
    (
        "imap_glows_l1a_raw_20231010_20231011_v01-03.pkts",
        False,
        (
            "Invalid extension. Extension should be pkts for data level l0 "
            "and cdf for data level higher than l0"
        ),
    ),
    (
        "imap_glows_l0__20231010_20231011_v01-04.pkts",
        False,
        (
            "Invalid filename. Filename convention is "
            "<mission>_<instrument>_<datalevel>_<descriptor>"
            "_<startdate>_<enddate>_<version>.<extension>"
        ),
    ),
    (
        "imap_hi-45_l0_raw_20231010_20231011_v01.pkts",
        False,
        "Invalid version format. Please use vxx-xx format.",
    ),
    (
        "imap_hi-45_l0_raw_20231010_20231011_v1-1.pkts",
        False,
        "Invalid version format. Please use vxx-xx format.",
    ),
    (
        "imap_hi-45_l3_raw_20231010_20231011_v01-01.cdf",
        False,
        f"Invalid data level. Please choose from {VALID_DATALEVELS}",
    ),
]


@pytest.mark.parametrize(("filename", "expected", "msg"), filename_and_expected_inputs)
def test_bad_filename(filename, expected, msg):
    """Validate filenames"""
    with pytest.raises(InvalidScienceFileError, match=msg):
        ScienceFilepathManager(filename)


good_filename = [
    ("imap_glows_l0_raw_20231010_20231011_v01-01.pkts", True, "Correct"),
    ("imap_hi-45_l0_raw_20231010_20231011_v01-06.pkts", True, "Correct"),
]


@pytest.mark.parametrize(("filename", "expected", "msg"), good_filename)
def test_good_filename(filename, expected, msg):
    science_file = ScienceFilepathManager(filename)

    assert science_file.is_valid == expected
    assert science_file.error_message == msg


def test_upload_filepath():
    """Test response from upload path function"""
    filename = "imap_glows_l0_raw_20231010_20231011_v01-01.pkts"
    upload_path = ScienceFilepathManager(filename).construct_upload_path()
    expected_path = f"imap/glows/l0/2023/10/{filename}"
    assert upload_path == expected_path


def test_missing_metadata():
    """Test missing filename metadata"""
    with pytest.raises(InvalidScienceFileError, match="Invalid filename. Expected"):
        ScienceFilepathManager("imap_glows_l0_raw_20231010_20231011")

    with pytest.raises(InvalidScienceFileError, match="Invalid filename. Expected"):
        ScienceFilepathManager("imap_glows_l0_raw_20231010_20231011_v01-01")
