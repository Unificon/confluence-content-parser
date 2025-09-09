from pydantic import BaseModel, Field


class UserReference(BaseModel):
    account_id: str | None = Field(None, alias="ri:account-id")
    local_id: str | None = Field(None, alias="ri:local-id")
    model_config = {"populate_by_name": True}


class PageReference(BaseModel):
    content_title: str = Field(..., alias="ri:content-title")
    space_key: str | None = Field(None, alias="ri:space-key")
    version_at_save: int | None = Field(None, alias="ri:version-at-save")
    model_config = {"populate_by_name": True}


class AttachmentReference(BaseModel):
    filename: str = Field(..., alias="ri:filename")
    content_id: str | None = Field(None, alias="ri:content-id")
    version_at_save: int | None = Field(None, alias="ri:version-at-save")
    model_config = {"populate_by_name": True}


class UrlReference(BaseModel):
    value: str = Field(..., alias="ri:value")
    model_config = {"populate_by_name": True}


class BlogPostReference(BaseModel):
    content_title: str = Field(..., alias="ri:content-title")
    space_key: str | None = Field(None, alias="ri:space-key")
    posting_day: str | None = Field(None, alias="ri:posting-day")
    model_config = {"populate_by_name": True}


class SpaceReference(BaseModel):
    space_key: str = Field(..., alias="ri:space-key")
    model_config = {"populate_by_name": True}


class ContentEntityReference(BaseModel):
    content_id: str = Field(..., alias="ri:content-id")
    model_config = {"populate_by_name": True}


class ShortcutReference(BaseModel):
    key: str = Field(..., alias="ri:key")
    parameter: str = Field(..., alias="ri:parameter")
    model_config = {"populate_by_name": True}


class Link(BaseModel):
    url: str | None = None
    user_reference: UserReference | None = None
    page_reference: PageReference | None = None
    attachment_reference: AttachmentReference | None = None
    url_reference: UrlReference | None = None
    blog_post_reference: BlogPostReference | None = None
    space_reference: SpaceReference | None = None
    content_entity_reference: ContentEntityReference | None = None
    shortcut_reference: ShortcutReference | None = None
    anchor: str | None = None
    card_appearance: str | None = Field(None, alias="data-card-appearance")
    text: str = ""
    model_config = {"populate_by_name": True}

    @property
    def kind(self) -> str | None:
        if self.user_reference:
            return "user"
        if self.page_reference:
            return "page"
        if self.blog_post_reference:
            return "blog_post"
        if self.space_reference:
            return "space"
        if self.attachment_reference:
            return "attachment"
        if self.content_entity_reference:
            return "content_entity"
        if self.shortcut_reference:
            return "shortcut"
        if self.url_reference or self.url:
            return "url"
        return None

    @property
    def canonical_uri(self) -> str | None:
        match self.kind:
            case "user":
                ref = self.user_reference
                if ref and ref.account_id:
                    return f"user://{ref.account_id}"
            case "page":
                pr = self.page_reference
                if pr is not None:
                    ct = pr.content_title
                    sk = pr.space_key or ""
                    if pr.version_at_save is not None:
                        return f"page://{sk}/{ct}@v{pr.version_at_save}"
                    return f"page://{sk}/{ct}"
            case "blog_post":
                bp = self.blog_post_reference
                if bp is not None:
                    return f"blog://{bp.space_key or ''}/{bp.content_title}@{bp.posting_day or ''}"
            case "space":
                space_ref = self.space_reference
                if space_ref is not None:
                    return f"space://{space_ref.space_key}"
            case "attachment":
                ar = self.attachment_reference
                if ar is not None:
                    ver = f"@v{ar.version_at_save}" if ar.version_at_save is not None else ""
                    return f"attach://{ar.filename}{ver}"
            case "content_entity":
                cer = self.content_entity_reference
                if cer is not None:
                    return f"contentid://{cer.content_id}"
            case "shortcut":
                shortcut_ref = self.shortcut_reference
                if shortcut_ref is not None:
                    return f"shortcut://{shortcut_ref.key}/{shortcut_ref.parameter}"
            case "url":
                if self.url_reference is not None:
                    return self.url_reference.value
                if self.url is not None:
                    return self.url
        return None
