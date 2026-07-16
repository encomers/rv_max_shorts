import asyncio
import logging

import httpx

from src.events import IEventBus
from src.model.domain import ReadyText

from .interface import IMessageSender
from .models.max_models import (
    Attachment,
    Payload,
    PublishPostRequest,
)

logger = logging.getLogger(__name__)


class MaxPublisher(IMessageSender):
    def __init__(
        self,
        base_url: str,
        token: str,
        chat_id: str | int,
        bus: IEventBus | None = None,
    ) -> None:
        self._base_url = base_url
        self._token = token
        self._chat_id = chat_id
        self._bus = bus
        if self._bus is not None:
            self._bus.subscribe(ReadyText, self._publish_ready_text_handler)

    async def _publish_ready_text_handler(self, event: ReadyText) -> None:
        try:
            await self.publish(event)
        except Exception as e:
            logger.error(f"Error publishing: {e}")
            event.enclosure = None
            await self.publish(event)

    async def publish(
        self,
        text: ReadyText,
    ) -> None:
        # image = (
        #     await self._upload_image(text.enclosure)
        #     if text.enclosure is not None
        #     else None
        # )
        await asyncio.sleep(3)
        publishing_text = f"<h1><a href='{text.link}'>{text.title}</a></h1>\n\n{text.text}\n\n<a href='https://max.ru/realnoevremya'>«Реальное время» в MAX</a>"
        attachment = (
            Attachment(
                type="image",
                payload=Payload(url=str(text.enclosure)),
            )
            if text.enclosure is not None
            else None
        )

        post_request = PublishPostRequest(
            text=publishing_text,
            attachments=[attachment] if attachment is not None else None,
        )
        url = self._base_url + f"/messages?chat_id={self._chat_id}"
        async with httpx.AsyncClient(timeout=20, verify=False) as client:
            try:
                response = await client.post(
                    url,
                    headers={"Authorization": f"{self._token}"},
                    json=post_request.model_dump(),
                )
                if response.status_code != 200:
                    print(text.link)
                    print(response.json())
                response.raise_for_status()
                logger.info("Post published successfully.")
            except Exception as e:
                logger.error(f"Failed to publish post: {e}")
                raise e
