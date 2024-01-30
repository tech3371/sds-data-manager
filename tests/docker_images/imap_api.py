"""Module for testing API utilities.
"""
import argparse
import json
import logging

import imap_data_access

logging.basicConfig(level=logging.INFO)


def _parse_args():
    """Parse the command line arguments.

    Returns
    -------
    args : argparse.Namespace
        An object containing the parsed arguments and their values
    """

    description = (
        "This command line program downloads"
        "a file from the file_path, modifies it, and uploads"
        "the modified file to the same s3 path. "
        "Example usage: python cli.py <file_path>. "
    )

    api_endpoint_help = (
        "The api_endpoint. Default is https://api.dev.imap-mission.com. "
    )

    parser = argparse.ArgumentParser(prog="imap_api", description=description)

    parser.add_argument(
        "--instrument", type=str, required=True, help="Instrument name."
    )
    parser.add_argument(
        "--level", type=str, required=True, help="Data processing level."
    )
    parser.add_argument(
        "--file_path",
        type=str,
        required=True,
        help="Full path to the file in the S3 bucket.",
    )
    parser.add_argument(
        "--dependency",
        type=json.loads,
        required=True,
        help="Dependency information in JSON format.",
    )
    parser.add_argument("--api_endpoint", type=str, help=api_endpoint_help)
    args = parser.parse_args()

    return args


def main():
    """Main function for the IMAP API utilities."""
    args = _parse_args()

    # Download file
    output_path = imap_data_access.download(args.file_path)
    # change filename
    remote_file_name = output_path.name

    # Modify descriptor in file name
    modified_file_name = remote_file_name.replace(
        remote_file_name[12:15], f"{remote_file_name[12:15]}-test"
    )
    new_path = output_path.parent / modified_file_name
    # Create an empty file
    new_path.touch(exist_ok=True)
    logging.info(f"renamed file {modified_file_name}")
    logging.info(f"new path - {new_path}")
    # upload renamed file
    imap_data_access.upload(new_path)

    logging.info("Process completed successfully")


if __name__ == "__main__":
    main()
