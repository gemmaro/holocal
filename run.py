import asyncio
import logging
import sys
from os import getenv

from dotenv import load_dotenv

import holodule.holodule

load_dotenv()
logging.basicConfig(
    level=(getenv("HOLODULE_LOGLEVEL") or "INFO").upper(),
    format="[{levelname}][{module}][{funcName}] {message}",
    style='{'
)

log = logging.getLogger()

if __name__ == "__main__":
    # argparse いる？ 使わなそう…
    holodule_page = getenv(
        "HOLODULE_PAGE") or "https://schedule.hololive.tv/simple"
    youtube_key = getenv("HOLODULE_YOUTUBE_KEY")
    save_dir = getenv("HOLODULE_DIR") or "public"

    if not holodule_page:
        log.critical("no holodule_page is given")
        sys.exit(1)

    if not youtube_key:
        log.critical("no youtube_key is given")
        sys.exit(1)

    h = holodule.holodule.Holodule(holodule_page, youtube_key, save_dir)
    sys.exit(asyncio.run(h.run()))
