import html
from datetime import datetime
from typing import Any, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class Enclosure(BaseModel):
    # Заменили Field(...) на Field(default=None), так как поле опциональное
    url: Optional[HttpUrl] = Field(
        default=None, description="URL изображения, если есть"
    )
    type: Optional[str] = Field(
        default=None, description="Тип вложения, например, 'image/jpeg'"
    )

    @field_validator("url", "type", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any):
        """
        Конвертируем пустые строки в None до валидации.
        Иначе Pydantic будет пытаться распарсить '' как URL и упадет с ошибкой.
        """
        if v == "":
            return None
        return v


class NewsItem(BaseModel):
    # Разрешаем обращаться к полям как по snake_case, так и по alias при создании
    model_config = ConfigDict(populate_by_name=True)

    title: str
    pub_date: str = Field(alias="pubDate")
    pub_time_parsed: datetime = Field(alias="pubTimeParsed")
    category: List[str]

    article_category: Optional[str] = Field(default=None, alias="articleCategory")
    link: HttpUrl
    amp_link: Optional[HttpUrl] = Field(default=None, alias="ampLink")
    description: str

    full_text: str = Field(alias="fullText")

    # Поле создается пустым, но заполняется автоматически через валидатор ниже
    parsed_full_text: Optional[str] = Field(default=None)

    enclosure: Optional[Enclosure] = None
    guid: str
    region: Optional[str] = None
    author: Optional[str] = None

    @model_validator(mode="after")
    def parse_html_entities(self) -> "NewsItem":
        """
        Автоматически конвертирует full_text в нормальный HTML.
        Стандартный модуль json сам справляется с юникодом (\u003c -> <),
        а html.unescape превращает HTML-сущности вроде &lt; обратно в теги < >.
        """
        if self.full_text:
            self.parsed_full_text = html.unescape(self.full_text)
        return self


class Channel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    link: HttpUrl
    description: str
    language: str
    codes: str


class KafkaNewsMessage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    news_item: NewsItem = Field(alias="newsItem")
    channel: Channel
    is_testing: bool = Field(default=False, alias="isTesting")
