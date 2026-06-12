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

        # async def _get_upload_server(self) -> HttpUrl | None:
        #     request_url = self._base_url + "/uploads?type=image"
        #     headers = {"Authorization": f"{self._token}"}
        #     try:
        #         async with httpx.AsyncClient(timeout=20) as client:
        #             response = await client.post(request_url, headers=headers)
        #             response.raise_for_status()
        #             data = UploadServerResponse.model_validate(response.json())
        #             return data.url
        #     except Exception as e:
        #         logger.error(f"Failed to get upload server: {e}")
        #         return None

        # async def _upload_image_to_server(
        #     self, url: HttpUrl, image_data: str
        # ) -> str | None:
        #     headers = {
        #         "Authorization": f"{self._token}",
        #     }

        #     if "," in image_data:
        #         image_data = image_data.split(",", 1)[1]
        #     binary_data = base64.b64decode(image_data)

        #     files = {"data": ("image.jpg", binary_data, "image/jpeg")}
        #     try:
        #         async with httpx.AsyncClient(timeout=20) as client:
        #             response = await client.post(str(url), headers=headers, files=files)
        #             response.raise_for_status()
        #             data = response.json()
        #             return data
        #     except Exception as e:
        #         logger.error(f"Failed to upload image to server: {e}")
        #         return None

        # async def _upload_image(self, image_url: HttpUrl) -> str | None:
        # try:
        #     base64_image = await to_base64_image(str(image_url))
        #     upload_url = await self._get_upload_server()
        #     if upload_url is None:
        #         return None
        #     token = await self._upload_image_to_server(upload_url, base64_image)
        #     return token
        # except Exception as e:
        #     logger.error(f"Failed to upload image: {e}")
        #     return None

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
        async with httpx.AsyncClient(timeout=20) as client:
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
