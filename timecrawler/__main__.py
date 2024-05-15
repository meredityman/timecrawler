import argparse
from timecrawler.timecrawler import TimeCrawler
from pathlib import Path
import datetime as datetime
import logging

logging.basicConfig(level=logging.INFO)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TimeCrawler")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--root_path", help="Root path for the diary", default="data")
    parser.add_argument("--input_dir", help="Input directory to get files from")
    args = parser.parse_args()

    root_path = Path(args.root_path)
    timecrawler = TimeCrawler(root_path)

    if args.command == "build":
       timecrawler.create_tree(datetime.date(2024, 1, 1), datetime.date.today())
    elif args.command == "info":
        logging.info(timecrawler.info())
    elif args.command == "clean":
        timecrawler.clean()
    elif args.command == "get_files":
        from timecrawler.get_files import get_files
        get_files(args, timecrawler)
    elif args.command == "get_deaths":
        from timecrawler.wikipedia import get_deaths
        get_deaths(args, timecrawler)
    elif args.command == "visualize":
        from timecrawler.visualize import visualize
        visualize(args, timecrawler)
    else:
        raise ValueError(f"Unknown command: {args.command}")