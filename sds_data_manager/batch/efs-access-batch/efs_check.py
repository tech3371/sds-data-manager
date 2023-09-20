import os

# Define the paths
attitude_symlink_path = "/mnt/spice/latest_attitude_kernel.ah.a"
ephemeris_symlink_path = "/mnt/spice/latest_ephemeris_kernel.bsp"


def spice_handler():
    """Read latest spice file

    Returns
    -------
    dict
        Status and message
    """

    # Check if the old symlink exists
    if os.path.islink(attitude_symlink_path):
        with open(os.path.realpath(attitude_symlink_path)) as f:
            content = f.read()
            print("Attitude kernel:\n", content)

    if os.path.islink(ephemeris_symlink_path):
        with open(os.path.realpath(ephemeris_symlink_path)) as f:
            content = f.read()
            print("Ephemeris kernel:\n", content)

    return {"statusCode": 200, "body": "Found symlink"}


if __name__ == "__main__":
    spice_handler()
