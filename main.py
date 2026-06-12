import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from src.events.event_bus import EventBus
from src.model.kafka import KafkaNewsMessage
from src.services.post_generator.factory import BaseFactory
from src.services.publisher.max_publisher import MaxPublisher
from src.services.reader.kafka_reader import KafkaReader

logger = logging.getLogger(__name__)

try:
    load_dotenv()  # reads variables from a .env file and sets them in os.environ
except Exception as e:
    logger.error(e)

MAX_CHANNEL_ID = os.getenv("MAX_CHANNEL_ID", "")
MAX_TOKEN = os.getenv("MAX_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "")

KAFKA_ADDR = os.getenv("KAFKA_ADDR", "")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "")


def is_within_last_hour(target_time: datetime) -> bool:
    """
    Проверяет, что разница между текущим временем и target_time меньше 1 часа.
    Всё время приводится к UTC.
    """
    # Текущее время в UTC
    now_utc = datetime.now(timezone.utc)

    # Если передано naive datetime (без tzinfo), считаем, что оно уже в UTC
    if target_time.tzinfo is None:
        target_utc = target_time.replace(tzinfo=timezone.utc)
    else:
        # Если aware — просто конвертируем в UTC
        target_utc = target_time.astimezone(timezone.utc)

    # Абсолютная разница, чтобы работало в обе стороны (прошлое и будущее)
    diff = abs(now_utc - target_utc)
    return diff < timedelta(hours=1)


def parsing_condition(msg: KafkaNewsMessage) -> bool:
    if "/news" not in str(msg.news_item.link):
        return False
    if "erid=" in str(msg.news_item.link):
        return False
    if msg.news_item.author is None or msg.news_item.author == "":
        return False
    if "*" in msg.news_item.title:
        return False

    return is_within_last_hour(msg.news_item.pub_time_parsed)


async def main():
    bus = EventBus()
    reader = KafkaReader(
        bootstrap_server=KAFKA_ADDR,
        topic=KAFKA_TOPIC,
        group_id=KAFKA_GROUP_ID,
        bus=bus,
    )
    facttory = BaseFactory(
        parsing_condition=parsing_condition,
        bus=bus,
    )
    publisher = MaxPublisher(
        base_url=BASE_URL,
        token=MAX_TOKEN,
        chat_id=MAX_CHANNEL_ID,
        bus=bus,
    )
    await reader.start_reading()


if __name__ == "__main__":
    asyncio.run(main())
