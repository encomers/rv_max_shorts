from abc import ABC, abstractmethod

from src.model.domain import ReadyText


class IMessageSender(ABC):
    @abstractmethod
    async def publish(
        self,
        text: ReadyText,
    ) -> None: ...
