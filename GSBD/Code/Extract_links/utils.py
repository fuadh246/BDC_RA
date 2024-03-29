import os
import logging
import argparse
import pandas as pd
from rich.logging import RichHandler


def debug_format(
    df: pd.DataFrame,
    out_path: str,
) -> None:
    csv, date, debug, filename = out_path.split('/')
    if not os.path.exists(os.path.join(csv, date, debug)):
        os.mkdir(os.path.join(csv, date, debug))
    df.to_csv(out_path)
    return


def arguements() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Get filing links and dates')
    parser.add_argument(
        '--url', type=str, required=False,
        default='https://www.sec.gov/edgar/browse/?CIK=1278752',
        help='Sec url to get links from'
    )
    parser.add_argument(
        '--url_txt', type=str, required=False,
        default='urls/1422183.txt',
        help='.txt to get links from'
    )
    # parser.add_argument(
    #     '--firefox-driver-path', type=str, required=False,
    #     default="geckodriver.exe",
    #     help='path to your geckodriver.exe'
    # )
    parser.add_argument(
        '--chrome-driver-path', type=str, required=False,
        default='/Users/fuadhassan/Desktop/BDC_RA/chromedriver_mac64/chromedriver',
        help='path to your geckodriver.exe'
    )
    parser.add_argument(
        '--firefox-path', type=str, required=False,
        default=r"C:\Program Files\WindowsApps\Mozilla.Firefox_116.0.3.0_x64__n80bbvh6b1yt2\VFS\ProgramFiles\Firefox Package Root\firefox.exe",
        help='path to your firefox.exe'
    )
    parser.add_argument(
        '--chrome-path', type=str, required=False,
        default=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        help='path to your chrome.exe'
    )
    return parser.parse_args()


def init_logger() -> None:
    logger = logging.getLogger("rich")
    logger.setLevel(logging.WARNING)
    logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
    logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('root').setLevel(logging.ERROR)

    FORMAT = "%(name)s[%(process)d] " + \
        "%(processName)s(%(threadName)s) " + \
        "%(module)s:%(lineno)d  %(message)s"

    formatter = logging.Formatter(
        FORMAT,
        datefmt="%Y%m%d %H:%M:%S"
    )
    logging.basicConfig(
        level="NOTSET", format=FORMAT, handlers=[RichHandler()]
    )

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    logging.info("Initializing ok.")
