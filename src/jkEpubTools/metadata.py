import uuid


class MetaData:
    def __init__(self, md_dict: dict[str, str] = {}) -> None:
        self.version = md_dict.get("version", "2.0")
        self.publisher = md_dict.get("publisher", None)
        self.rights = md_dict.get("rights", None)
        self.language = md_dict.get("language", None)
        self.author = md_dict.get("author", None)
        self.author_sortname = md_dict.get("author_sortname", None)
        self.title = md_dict.get("title", None)
        # path to image file:
        self.cover = md_dict.get("cover", None)
        # mime type of cover image file:
        self.cover_type = md_dict.get("cover_type", None)
        self.date = md_dict.get("date", None)
        self.uuid = md_dict.get("uuid", uuid.uuid1())
        self.subject = md_dict.get("subject", None)
