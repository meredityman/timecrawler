from pathlib import Path
import logging
from datetime import datetime, timedelta
from collections import OrderedDict
import shutil
import json

class Channel:

    def __init__(self, name, files, data):
        self.name  = name
        self.files = files
        self.data  = data

    def json(self):
        return {
            "name": self.name,
            "files": [str(f) for f in self.files],
            "data": self.data
        }

class Day:

    def __init__(self, date, root_path):
        self.date = date
        self.channels = {}

        year  = date.strftime("%Y")
        month = date.strftime("%B")

        timestamp = date.strftime("%Y-%m-%d")
        dirname = f"{timestamp}_{date.strftime('%A')}"
        directory = Path(root_path, year, month, dirname)
        if(directory.exists()):
            logging.debug(f"Directory already exists: {directory}")
        else:
            logging.info(f"Creating folder for {timestamp}")
            directory.mkdir(parents=True)

        self.timestamp = timestamp 
        self.directory = directory

        self.meta_path = Path(directory, "metadata.json")
        if(self.meta_path.exists()):
            self._load_metadata()
        else:
            logging.info(f"Creating metadata file: {self.meta_path}")
            self._save_metadata()

    def _load_metadata(self):
        try:
            with open(self.meta_path, "r") as f:
                metadata = json.load(f)
                self.channels = {}
                for c in metadata["channels"]:
                    self.channels[c] = Channel(c, metadata["channels"][c]["files"], metadata["channels"][c]["data"])

        except Exception as e:
            logging.error(f"Error loading metadata: {e}")
            self._save_metadata()


    def _save_metadata(self):
        metadata = {
            "timestamp": self.timestamp,
            "directory": str(self.directory),
            "channels": {n: c.json() for n, c in self.channels.items()} if self.channels is not None else {}
        }
        with open(self.meta_path, "w") as f:
            json.dump(metadata, f, indent=4)

    def update_channel(self, channel, files, data):
        for file in files:
            if not file.exists():
                logging.error(f"File does not exist: {file}")
                raise FileNotFoundError(f"File does not exist: {file}")
            if file.parent != self.directory:
                logging.error(f"File not in directory: {file}")
                raise FileNotFoundError(f"File not in directory: {file}")
            
        self.channels[channel] = Channel(channel, files, data)

        self._save_metadata()


    def get_channel_data(self, channel):
        if channel in self.channels:
            return self.channels[channel].json()
        else:
            return None

    def info(self):
        info = f"Day: {self.date}\n"
        for channel in self.channels.values():
            print(channel)
            info += f"\tChannel: {channel.name}\n"
            info += f"\tFiles: {channel.files}\n"
            info += f"\tData: {channel.data}\n"

        return info

class TimeCrawler:
    def __init__(self, root_path):

        self.start_date = None
        self.end_date = None

        root_path = Path(root_path)
        parent_path = root_path.parent
        if not parent_path.exists() or not parent_path.is_dir():
            logging.error(f"Path does not exist: {parent_path}")
            raise FileNotFoundError(f"Path does not exist: {parent_path}")

        self.root_path = root_path
        self.days = OrderedDict()

        if self.root_path.exists():
            self.load_tree()

        logging.info(f"TimeCrawler initialized with root path: {self.root_path}")
        logging.info(f"Period: {self.start_date} - {self.end_date}")


    def __iter__(self):
        return iter(self.days.values())

    def __next__(self):
        return next(self.days.values())
    
    def __getitem__(self, key):
        return self.days[key]

    def __len__(self):
        return len(self.days)

    def info(self):
        info = f"TimeCrawler: {self.root_path}, {self.start_date} - {self.end_date}\n"
        for day in self.days.values():
            info += day.info()
        return info

    def clean(self):
        logging.warning(f"Cleaning root path: {self.root_path}")
        ret = input("Are you sure you want to delete all data? (y/n): ")
        if ret.lower() != "y":
            logging.warning("Aborting clean")
            return
        
        shutil.rmtree(self.root_path)
        self = TimeCrawler(self.root_path)

    def create_tree(self, start_date: datetime.date, end_date: datetime.date):

        assert(start_date <= end_date)

        self.start_date = start_date
        self.end_date = end_date

        dates = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        for date in dates:
            timestamp = date.strftime("%Y-%m-%d")
            self.days[timestamp] = Day(date, self.root_path)



    def dates(self):
        return self.days.keys()

    def load_tree(self):
        for year in self.root_path.iterdir():
            if not year.is_dir():
                continue
            for month in year.iterdir():
                if not month.is_dir():
                    continue
                for day in month.iterdir():
                    if not day.is_dir():
                        continue
                    date = datetime.strptime(day.name.split("_")[0], "%Y-%m-%d").date()
                    timestamp = date.strftime("%Y-%m-%d")
                    self.days[timestamp] = Day(date, self.root_path)
        if len(self.days) > 0:
            self.start_date = datetime.strptime(min(self.days.keys()), "%Y-%m-%d").date()
            self.end_date   = datetime.strptime(max(self.days.keys()), "%Y-%m-%d").date()

