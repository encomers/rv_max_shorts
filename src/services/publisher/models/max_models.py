from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class UploadServerResponse(BaseModel):
    url: HttpUrl = Field(..., description="URL для загрузки изображения на сервер Max")


class UploadImageResponse(BaseModel):
    token: str = Field(..., description="URL загруженного изображения на сервере Max")


class Payload(BaseModel):
    url: str = Field(
        ..., description="Токен изображения, полученный после загрузки на сервер Max"
    )
    token: str | None = None
    photos: Any | None = None


class Attachment(BaseModel):
    type: str = Field(..., description="Тип вложения, например, 'image'")
    payload: Payload = Field(
        ..., description="Детали вложения, включая токен изображения"
    )


class PublishPostRequest(BaseModel):
    text: str = Field(..., description="Текст поста")
    attachments: list[Attachment] | None = Field(
        ..., description="Список вложений для поста, например, изображений"
    )
    format: str = Field(default="html")
