from dataclasses import dataclass


@dataclass
class ProcessedFile:
    id: str
    name: str
    share_link: str
    download_link: str
    processed_time: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "share_link": self.share_link,
            "download_link": self.download_link,
            "processed_time": self.processed_time,
        }
