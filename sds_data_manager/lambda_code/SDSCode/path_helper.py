"""Functions to store file pattern, validate and construct upload path
"""
import re
from datetime import datetime

VALID_INSTRUMENTS = {
    "codice",
    "glows",
    "hit",
    "hi-45",
    "hi-90",
    "idex",
    "lo",
    "mag",
    "swapi",
    "swe",
    "ultra-45",
    "ultra-90",
}

VALID_DATALEVELS = {"l0", "l1", "l1a", "l1b", "l1c", "l1d", "l2"}

VALID_FILE_EXTENSION = {"pkts", "cdf"}


class InvalidScienceFileError(Exception):
    """Indicates a bad file type"""

    pass


class ScienceFilepathManager:
    def __init__(self, filename):
        """Class to store file pattern

        Current filename convention:
        <mission>_<instrument>_<datalevel>_<descriptor>_<startdate>_<enddate>_<version>.<extension>

        NOTE: There are no optional parameters anymore. All parameters are required.
        <mission>: imap
        <instrument>: idex, swe, swapi, hi-45, ultra-45 and etc.
        <datalevel> : l1a, l1b, l1, l3a and etc.
        <descriptor>: descriptor stores information specific to instrument. This is
            decided by each instrument.
        <startdate>: startdate is the earliest date in the data. Format - YYYYMMDD
        <enddate>: Some instrument and some data level requires to store date range.
            If there is no end date, then startdate will be used as enddate as well.
            Format - YYYYMMDD.
        <version>: This stores software version and data version. Version format is
            vxx-xx.

        Parameters
        ----------
        filename : str
            Science data filename
        """
        # TODO: refactor this post demo
        self.filename = filename
        split_filename = self.filename.split("_")
        filename_convention = (
            "<mission>_<instrument>_<datalevel>_<descriptor>_"
            "<startdate>_<enddate>_<version>.<extension>"
        )

        if len(split_filename) != 7:
            raise InvalidScienceFileError(
                f"Invalid filename. Expected - {filename_convention}"
            )

        (
            self.mission,
            self.instrument,
            self.data_level,
            self.descriptor,
            self.startdate,
            self.enddate,
            last_value,
        ) = split_filename
        if "." not in last_value:
            raise InvalidScienceFileError(
                f"Invalid filename. Expected - {filename_convention}"
            )

        (self.version, self.extension) = last_value.split(".")

        (self.is_valid, self.error_message) = self.is_filename_valid()

        if not self.is_valid:
            raise InvalidScienceFileError(f"{self.error_message}")

    def check_date_input(self, input_date: str) -> bool:
        """Check input date string is in valid format and is correct date

        Parameters
        ----------
        input_date : str
            Date in YYYYMMDD format.

        Returns
        -------
        bool
            Whether date input is valid or not
        """

        # Validate if it's a real date
        try:
            # This checks if date is in YYYYMMDD format.
            # Sometimes, date is correct but not in the format we want
            if len(input_date) != 8:
                raise ValueError("Invalid date format. Expected - YYYYMMDD")
            datetime.strptime(input_date, "%Y%m%d")
            return True
        except ValueError:
            return False

    def is_filename_valid(self):
        """Check if filename is in valid format.

        Returns
        -------
        bool
            Whether filename is valid or not
        str
            Error message or "Correct"
        """

        filename_convention = (
            "<mission>_<instrument>_<datalevel>_<descriptor>_"
            "<startdate>_<enddate>_<version>.<extension>"
        )

        # First check if any of parameter is missing
        if any(
            attr is None or attr == ""
            for attr in [
                self.mission,
                self.instrument,
                self.data_level,
                self.descriptor,
                self.startdate,
                self.enddate,
                self.version,
                self.extension,
            ]
        ):
            default_message = (
                f"Invalid filename. Filename convention is {filename_convention}"
            )
            return False, default_message

        # Dictionary to map fields to their valid values and error messages
        validation_checks = {
            "mission": (
                self.mission == "imap",
                "Invalid mission.",
            ),
            "instrument": (
                self.instrument in VALID_INSTRUMENTS,
                ("Invalid instrument. Please choose from " f"{VALID_INSTRUMENTS}"),
            ),
            "data_level": (
                self.data_level in VALID_DATALEVELS,
                ("Invalid data level. Please choose from " f"{VALID_DATALEVELS}"),
            ),
            "startdate": (
                self.check_date_input(self.startdate),
                "Invalid start date format. Please use YYYYMMDD format.",
            ),
            "enddate": (
                self.check_date_input(self.enddate),
                "Invalid end date format. Please use YYYYMMDD format.",
            ),
            "version": (
                bool(re.match(r"^v\d{2}-\d{2}$", self.version)),
                "Invalid version format. Please use vxx-xx format.",
            ),
            "extension": (
                self.extension in VALID_FILE_EXTENSION
                and (
                    (self.data_level == "l0" and self.extension == "pkts")
                    or (self.data_level != "l0" and self.extension == "cdf")
                ),
                (
                    "Invalid extension. Extension should be pkts for data level l0 "
                    "and cdf for data level higher than l0"
                ),
            ),
        }

        # Iterate through each validation check
        for _, (is_valid, error_message) in validation_checks.items():
            if not is_valid:
                return False, error_message

        return True, "Correct"

    def construct_upload_path(self):
        """Construct upload path

        Returns
        -------
        str
            Upload path
        """
        upload_path = (
            f"{self.mission}/{self.instrument}/{self.data_level}/"
            f"{self.startdate[:4]}/{self.startdate[4:6]}/{self.filename}"
        )

        return upload_path

    def get_file_metadata_params(self):
        """Get file metadata parameters

        Returns
        -------
        dict
            File metadata parameters
        """

        return {
            "file_path": None,
            "instrument": self.instrument,
            "data_level": self.data_level,
            "descriptor": self.descriptor,
            "start_date": datetime.strptime(self.startdate, "%Y%m%d"),
            "end_date": datetime.strptime(self.enddate, "%Y%m%d"),
            "version": self.version,
            "extension": self.extension,
        }
