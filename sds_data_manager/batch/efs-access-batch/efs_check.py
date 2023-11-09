from pathlib import Path

# Define the paths
attitude_symlink_path = "/mnt/spice/latest_attitude_kernel.ah.a"
ephemeris_symlink_path = "/mnt/spice/latest_ephemeris_kernel.bsp"


def spice_handler():
    """Read latest spice file.

    This function is a place holder for future L1A or L1B code.
    This function and code is showing that we can read latest
    spice file from EFS through batch job.

    Returns
    -------
    dict
        Status and message
    """

    # Check if the old symlink exists
    if Path.is_symlink(attitude_symlink_path):
        # Path.resolve() returns the absolute path of the symlink
        with open(Path.resolve(attitude_symlink_path)) as f:
            content = f.read()
            print("Attitude kernel:\n", content)

    if Path.is_symlink(ephemeris_symlink_path):
        with open(Path.resolve(ephemeris_symlink_path)) as f:
            content = f.read()
            print("Ephemeris kernel:\n", content)

    return {"statusCode": 200, "body": "Found symlink"}


if __name__ == "__main__":
    spice_handler()
