import datetime
import enum
import html.parser
import logging
import re

from holodule.errors import HoloduleException
from holodule.event import Event, Talent, Type

YOUTUBE_URL = r"https://www[.]youtube[.]com/watch[?]v=(?P<id>[A-Za-z0-9_-]+)"
TWITCH_URL = r"https://www[.]twitch[.]tv/[a-z_]+"
SPACES_WITH_NEWLINES = r"[ \r]*\n[ \n\r]*"
DATE = r"(?P<month>\d\d)/(?P<day>\d\d)"
TIME = r"(?P<hour>\d\d):(?P<minute>\d\d)"

log = logging.getLogger(__name__)


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._state = State.OUTSIDE
        self._tags = []
        self.events = []
        self._reset_current_link()

    def handle_starttag(self, tag, attrs):
        match self._state:
            case State.OUTSIDE:
                if dict(attrs).get("id") == "all":
                    self._state = State.INSIDE

            case State.INSIDE:
                self._tags.append(tag)
                if tag == "a":
                    self.current_hyperlink = dict(attrs)["href"]
                    self._state = State.ANCHOR

                if tag == "div" and \
                   dict(attrs).get("class") == "holodule navbar-text":
                    self._state = State.DATE

            case State.ANCHOR:
                if tag != "img":
                    self._tags.append(tag)

            case State.REST:
                pass

            case _:
                raise HoloduleException()

    def handle_data(self, data):
        if self._state == State.ANCHOR:
            self.current_text += data

        elif self._state == State.DATE:
            match data.split():
                case [date, _]:
                    match = re.match(DATE, date)
                    if not match:
                        raise HoloduleException(repr(date))

                    self._date = Date(int(match["month"]), int(match["day"]))

    def handle_endtag(self, tag):
        match self._state:
            case State.OUTSIDE | State.REST:
                pass

            case State.INSIDE:
                if not self._tags:
                    self._state = State.REST
                    return

                top = self._tags.pop()
                if tag != top:
                    raise HoloduleException()

            case State.ANCHOR if self._tags.pop() == tag:
                if tag == "a":
                    self._parse_anchor_text()
                    self._reset_current_link()
                    self._state = State.INSIDE

            case State.DATE if self._tags.pop() == tag:
                self._state = State.INSIDE

            case _:
                raise HoloduleException()

    def _reset_current_link(self):
        self.current_hyperlink = None
        self.current_text = ""

    def _parse_anchor_text(self):
        words = re.split(SPACES_WITH_NEWLINES, self.current_text)
        match words:
            case ['', time, talent, '']:
                self._validate_time(time)
                self._append_link(url=self.current_hyperlink,
                                  talent=Talent(talent))

            case ['', time, talent, mark, '']:
                self._validate_time(time)
                self._append_link(url=self.current_hyperlink,
                                  talent=Talent(talent, mark))

            case _:
                raise HoloduleException(f"text: {repr(words)}")

    def _validate_time(self, time):
        match = re.match(TIME, time)
        if not match:
            raise HoloduleException(repr(time))

        year = int(match["hour"])
        minute = int(match["minute"])
        time = Time(year, minute)
        self._time = time

    def _append_link(self, url, talent):
        year = datetime.datetime.now().year
        tzone = datetime.timezone(datetime.timedelta(hours=9))
        time = datetime.datetime(year,
                                 self._date.month,
                                 self._date.day,
                                 self._time.hour,
                                 self._time.minute,
                                 tzinfo=tzone)
        time = time.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
        self.events.append(Event(site=Site.parse_url(url),
                                 talent=talent,
                                 datetime=time))


class Site:
    def parse_url(url):
        match = re.search(YOUTUBE_URL, url)
        if match:
            return Site(url, id=match["id"])

        elif url == 'https://abema.app/hfAA':
            return Site(url, type=Type.Abema)

        elif re.match(TWITCH_URL, url):
            return Site(url, type=Type.Twitch)

        else:
            raise HoloduleException(f"unmatch: {repr(url)}")

    def __init__(self, url, type=Type.YouTube, id=None):
        self.url = url
        self.type = type
        self.id = id

    def __repr__(self):
        return f"<{self.type} {self.id or self.url}>"


class Date:
    def __init__(self, month, day):
        self.month = month
        self.day = day


class Time:
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute


class State(enum.Enum):
    OUTSIDE = "outside of anchors"
    INSIDE = "inside of anchors"
    ANCHOR = "reading anchor text"
    REST = "rest, after anchors"
    DATE = "date"
