import datetime
import enum
import html.parser
import logging
import re
import unicodedata

import ics

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
                raise Error()

    def handle_data(self, data):
        if self._state == State.ANCHOR:
            self.current_text += data

        elif self._state == State.DATE:
            match data.split():
                case [date, _]:
                    match = re.match(DATE, date)
                    if not match:
                        raise Error(repr(date))

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
                    raise Error()

            case State.ANCHOR:
                while (top := self._tags.pop()) != tag:
                    raise Error(f"{tag} and {top} when {self._state} "
                                f"({repr(self._tags)})")

                if tag == "a":
                    self._parse_anchor_text()
                    self._reset_current_link()
                    self._state = State.INSIDE

            case State.DATE:
                if self._tags.pop() != tag:
                    raise Error()

                self._state = State.INSIDE

            case _:
                raise Error()

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
                raise Error(f"text: {repr(words)}")

    def _validate_time(self, time):
        match = re.match(TIME, time)
        if not match:
            raise Error(repr(time))

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


class Talent:
    def __init__(self, name, mark=None):
        # "So" means "Other Symbol" (emoji)
        if mark and any(unicodedata.category(char) != "So" for char in mark):
            raise Error()

        self.name = name
        self.mark = mark

    def __str__(self):
        mark = self.mark or ""
        return f"{mark}{self.name}"

    def __repr__(self):
        if self.mark:
            return f"<{self.name} {self.mark}>"

        else:
            return f"<{self.name}>"


class Event:
    def __init__(self, site, talent: Talent, datetime):
        self.site = site
        self.talent = talent
        self.datetime = datetime
        self.show = True
        self.end = None

    def ical_event(self) -> ics.Event:
        kwargs = {}
        if self.end:
            kwargs["end"] = self.end

        else:
            kwargs["duration"] = {"hours": 2}

        return ics.Event(
            name=f"{self.talent.name}: {self.title}",
            begin=self.datetime,
            description=f"{self.title}\n{self.site.url}",
            # use video_id as uid will make order of events static
            # (because uid is used in Event.__hash__)
            uid=self.site.id,  # TODO: コラボで同じ動画が複数ホロジュールに登録される可能性？
            **kwargs,
        )

    def assign(self, meta: dict) -> bool:
        end_time = None

        match meta:
            # "publishedAt" is for video case.
            # TODO: is this correct?
            case {"snippet": {"title": title},
                  "liveStreamingDetails": {"actualStartTime": time,
                                           "actualEndTime": end_time}}:
                pass

            case {"snippet": {"title": title},
                  "liveStreamingDetails": {"scheduledStartTime": time}} \
                    | {"snippet": {"title": title, "publishedAt": time}}:
                log.debug(repr(meta))
                pass

            case None:
                match self.site.type:
                    case Type.Twitch | Type.Abema:
                        self.title = self.site.type.name
                        return

                    case Type.YouTube:
                        log.warn("Possibly private video?  "
                                 "Empty metadata.  "
                                 f"{repr(self)}")
                        self.show = False
                        return

        if not title or not time:
            raise Error(f"missing value: {repr(meta)}")

        self.title = title
        self.begin = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")

        if end_time:
            self.end = datetime.datetime.strptime(end_time,
                                                  "%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return f"<{self.site}\t{self.talent}\t{self.datetime}>"


class Type(enum.Enum):
    YouTube = "YouTube"
    Abema = "Abema"
    Twitch = "Twitch"


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
            raise Error(f"unmatch: {repr(url)}")

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


class Error(Exception):
    pass


class State(enum.Enum):
    OUTSIDE = "outside of anchors"
    INSIDE = "inside of anchors"
    ANCHOR = "reading anchor text"
    REST = "rest, after anchors"
    DATE = "date"
