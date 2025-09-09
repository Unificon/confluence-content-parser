from pydantic import BaseModel

from .links import AttachmentReference, UrlReference


class Image(BaseModel):
    alt: str | None = None
    title: str | None = None
    width: str | None = None
    height: str | None = None
    alignment: str | None = None
    layout: str | None = None
    original_height: str | None = None
    original_width: str | None = None
    custom_width: bool = False
    attachment_reference: AttachmentReference | None = None
    url_reference: UrlReference | None = None
