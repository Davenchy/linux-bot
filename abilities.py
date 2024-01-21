import os
import json
from datetime import datetime
from assistant import Assistant


@Assistant.ability()
def get_date_and_time():
    """Get date and time"""
    now = datetime.now()

    return "hour: {}, minute: {}, second: {}, day: {}, month: {}, year: {}".format(
        now.hour, now.minute, now.second, now.day, now.month, now.year
    )


@Assistant.ability(path="the path where the files to list are located")
def get_files(path: str) -> str:
    """return a list of files in specific path"""
    try:
        files = os.listdir(os.path.expanduser(path))
        return json.dumps(", ".join([file for file in files]))
    except Exception:
        return "Error: Failed to get files list"
