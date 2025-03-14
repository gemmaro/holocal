from datetime import datetime
from logging import getLogger

from ics import Event

log = getLogger(__name__)


class LiveEvent():
    def __init__(self, name: str, url: str, video_id=None) -> None:
        self.name = name
        self.url = url
        self.video_id = video_id

        self.title = None
        self.begin = None

    @property
    def ical_event(self) -> Event:
        return Event(
            name=f"{self.name}: {self.title}",
            begin=self.begin,
            duration={"hours": 2},
            description=f"{self.title}\n{self.url}",
            # use video_id as uid will make order of events static
            # (because uid is used in Event.__hash__)
            uid=self.video_id  # TODO: コラボで同じ動画が複数ホロジュールに登録される可能性？
        )

    def assign(self, meta: dict) -> bool:
        match meta:
            # "publishedAt" is for video case.
            # TODO: is this correct?
            case {"snippet": {"title": title},
                  "liveStreamingDetails": {"scheduledStartTime": time}} \
               | {"snippet": {"title": title},
                  "liveStreamingDetails": {"actualStartTime": time}} \
               | {"snippet": {"title": title, "publishedAt": time}}:
                pass

            case _:
                log.error(f"unexpected meta: {repr(meta)}")
                return False

        if not title or not time:
            log.error(f"missing value: {repr(meta)}")
            return False

        self.title = title
        self.begin = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        return True
