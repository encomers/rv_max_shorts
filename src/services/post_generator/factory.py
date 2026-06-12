import logging
from typing import Callable

from src.events import IEventBus
from src.model.domain import ReadyText
from src.model.kafka import KafkaNewsMessage

from .interface import IContentFactory

logger = logging.getLogger(__name__)


class BaseFactory(IContentFactory):
    def __init__(
        self,
        *,
        parsing_condition: Callable[[KafkaNewsMessage], bool] | None = None,
        bus: IEventBus | None = None,
    ) -> None:
        self.parsing_condition = parsing_condition
        self._bus = bus

        if self._bus is not None:
            self._bus.subscribe(bytes, self._complete_bytes_handler)

    async def _complete_bytes_handler(self, event: bytes) -> None:
        logger.info("ContentFactory get event")
        try:
            data = await self.complete_data(event)
            if self._bus is not None and data is not None:
                logger.info("ContentFactory send to event bus")
                await self._bus.publish(data)
        except Exception as e:
            logger.error(f"Ошибка обработки bytes: {e}")

    async def parse_bytes(self, data: bytes) -> KafkaNewsMessage | None:
        try:
            # 1. Десериализация и валидация
            event = KafkaNewsMessage.model_validate_json(data)

            # 2. Проверка пользовательского условия фильтрации
            if self.parsing_condition and not self.parsing_condition(event):
                logger.info(f"Event {event} does not pass parsing condition")
                return None

            return event

        except Exception as e:
            logger.error(f"Failed to parse raw text: {e}")
            raise e

    async def complete_message(self, message: KafkaNewsMessage) -> ReadyText:
        return ReadyText(
            title=message.news_item.title,
            text=message.news_item.description,
            link=message.news_item.link,
            enclosure=message.news_item.enclosure.url
            if message.news_item.enclosure is not None
            else None,
        )
