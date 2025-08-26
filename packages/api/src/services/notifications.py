from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from .smtp import send_smtp_notification

class Context():
    def __init__(self, strategy: NotificationStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> NotificationStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: NotificationStrategy) -> None:
        self._strategy = strategy

    def send_notification(self, notification: AlertNotification) -> AlertNotification:
        return self._strategy.send_notification(self, AlertNotification)


class NotificationStrategy(ABC):
    @abstractmethod
    def send_notification(self, notification: AlertNotification) -> AlertNotification:
        pass


class SmtpStrategy(NotificationStrategy):
    def send_notification(self, notification: AlertNotification) -> AlertNotification:
        return send_smtp_notification(notification)
