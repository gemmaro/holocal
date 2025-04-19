import datetime
import enum
import logging
import unicodedata

import ics

from holodule.errors import HoloduleException

log = logging.getLogger(__name__)


class Event:
    def __init__(self, site, talent, datetime):
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
            raise HoloduleException(f"missing value: {repr(meta)}")

        self.title = title
        self.begin = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")

        if end_time:
            self.end = datetime.datetime.strptime(end_time,
                                                  "%Y-%m-%dT%H:%M:%SZ")

    def __repr__(self):
        return f"<{self.site}\t{self.talent}\t{self.datetime}>"


class Talent:
    def __init__(self, name, mark=None):
        # "So" means "Other Symbol" (emoji)
        if mark and any(unicodedata.category(char) != "So" for char in mark):
            raise HoloduleException()

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
