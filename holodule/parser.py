import enum
import html.parser
import re
import unicodedata

YOUTUBE_URL = r"https://www[.]youtube[.]com/watch[?]v=(?P<id>[A-Za-z0-9_-]+)"
TWITCH_URL = r"https://www[.]twitch[.]tv/[a-z_]+"
SPACES_WITH_NEWLINES = r"[ \r]*\n[ \n\r]*"


# Extract dates to retrieve complete datetime?  Currently only time
# (hour:minute) can be extracted.
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

            case State.ANCHOR:
                self._tags.append(tag)

            case State.REST:
                pass

            case _:
                raise Error()

    def handle_data(self, data):
        if self._state == State.ANCHOR:
            self.current_text += data

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
                    if top != "img":
                        raise Error(f"{tag} and {top} when {self._state} "
                                    f"({repr(self._tags)})")

                if tag == "a":
                    self._parse_anchor_text()
                    self._reset_current_link()
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
        if not re.match(r"\d\d:\d\d", time):
            raise Error()

    def _append_link(self, url, talent):
        self.events.append(Event(site=Site.parse_url(url),
                                 talent=talent))


class Event:
    def __init__(self, site, talent):
        self.site = site
        self.talent = talent

    def __repr__(self):
        return f"<{self.site}\t{self.talent}>"


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


class Error(Exception):
    pass


class State(enum.Enum):
    OUTSIDE = "outside of anchors"
    INSIDE = "inside of anchors"
    ANCHOR = "reading anchor text"
    REST = "rest, after anchors"
