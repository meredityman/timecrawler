from pathlib import Path
from collections import defaultdict
import logging
from datetime import datetime
import random

def get_files(args, timecrawler):
    import shutil
    assert(args.input_dir is not None)

    input_dir = Path(args.input_dir)
    assert(input_dir.exists() and input_dir.is_dir())

    creation_dates = defaultdict(list)
    for file in Path(input_dir ).glob("*"):
        if file.is_file():
            date = datetime.fromtimestamp(file.stat().st_ctime)
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            timestamp = date.strftime("%Y-%m-%d")
            creation_dates[timestamp].append(file.absolute())
            logging.debug(f"File: {file} -> {timestamp}")

    for day in timecrawler:
        # print(date)
        timestamp = day.timestamp
        if timestamp in creation_dates:
            candidates = creation_dates[timestamp]
            random_file = candidates[random.randint(0, len(candidates) - 1)]
            file_path = Path(day.directory, f"get_files_{input_dir.name}{random_file.suffix}")
            shutil.copy(random_file, file_path)
            logging.info(f"File copied: {random_file} -> {file_path}")
            day.update_channel("get_files", [file_path], {
                "source": str(random_file)
            })
        else:
            pass
            # logging.warning(f"No files for '{date}'")
        