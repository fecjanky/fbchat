import attr
from ._core import Image
from . import _util


@attr.s
class Attachment:
    """Represents a Facebook attachment."""

    #: The attachment ID
    uid = attr.ib(None)


@attr.s
class UnsentMessage(Attachment):
    """Represents an unsent message attachment."""


@attr.s
class ShareAttachment(Attachment):
    """Represents a shared item (e.g. URL) attachment."""

    #: ID of the author of the shared post
    author = attr.ib(None)
    #: Target URL
    url = attr.ib(None)
    #: Original URL if Facebook redirects the URL
    original_url = attr.ib(None)
    #: Title of the attachment
    title = attr.ib(None)
    #: Description of the attachment
    description = attr.ib(None)
    #: Name of the source
    source = attr.ib(None)
    #: The attached image
    image = attr.ib(None)
    #: URL of the original image if Facebook uses ``safe_image``
    original_image_url = attr.ib(None)
    #: List of additional attachments
    attachments = attr.ib(factory=list, converter=lambda x: [] if x is None else x)

    # Put here for backwards compatibility, so that the init argument order is preserved
    uid = attr.ib(None)

    @classmethod
    def _from_graphql(cls, data):
        from . import _file

        url = data.get("url")
        rtn = cls(
            uid=data.get("deduplication_key"),
            author=data["target"]["actors"][0]["id"]
            if data["target"].get("actors")
            else None,
            url=url,
            original_url=_util.get_url_parameter(url, "u")
            if "/l.php?u=" in url
            else url,
            title=data["title_with_entities"].get("text"),
            description=data["description"].get("text")
            if data.get("description")
            else None,
            source=data["source"].get("text") if data.get("source") else None,
            attachments=[
                _file.graphql_to_subattachment(attachment)
                for attachment in data.get("subattachments")
            ],
        )
        media = data.get("media")
        if media and media.get("image"):
            image = media["image"]
            rtn.image = Image._from_uri(image)
            rtn.original_image_url = (
                _util.get_url_parameter(rtn.image.url, "url")
                if "/safe_image.php" in rtn.image.url
                else rtn.image.url
            )
        return rtn
