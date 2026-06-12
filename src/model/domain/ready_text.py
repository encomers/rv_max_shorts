from pydantic import BaseModel, Field, HttpUrl


class ReadyText(BaseModel):
    title: str = Field(..., description="Заголовок поста, если нужен")
    text: str = Field(..., min_length=1, description="Весь текст поста без заголовка")
    enclosure: HttpUrl | None = Field(
        ..., description="Выбранное изображение для поста"
    )
    link: HttpUrl | None = Field(
        None, description="Ссылка на источник новости, если нужно добавить"
    )
