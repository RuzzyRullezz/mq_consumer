import multiprocessing
from typing import Optional, Type
from abc import ABCMeta, abstractmethod

import pika
from .connectors import Connector
from .consumers import Consumer
from .mime_types import MqMimeTypesEnum
from .publishers import Publisher


class BaseConsumer(metaclass=ABCMeta):
    consumer_type: Type[Consumer] = NotImplemented
    connector_type: Type[Connector] = NotImplemented
    connection_params: pika.ConnectionParameters = NotImplemented

    exchange: str = NotImplemented
    exchange_type: str = NotImplemented
    routing_key: Optional[str] = None
    queue: str = NotImplemented

    mime_type: MqMimeTypesEnum = NotImplemented

    # instance properties
    consumer: Consumer

    def __init__(self, *args, **kwargs):
        self.consumer = self.consumer_type(self.get_connector(), self.handle, *args, **kwargs)

    @abstractmethod
    def handle(self, channel, method, properties, body):
        raise NotImplementedError

    @classmethod
    def get_connector(cls):
        properties = (
            'connection_params', 'exchange', 'exchange_type', 'queue'
        )
        for prop in properties:
            prop_value = getattr(cls, prop, None)
            assert prop_value is not None, f'Define property "{prop}" in BaseConsumer subclass first.'

        return cls.connector_type(
            cls.connection_params,
            cls.exchange,
            cls.queue,
            exchange_type=cls.exchange_type,
            routing_key=cls.routing_key,
        )

    @classmethod
    def create_publisher(cls) -> Publisher:
        if cls.mime_type is NotImplemented:
            raise Exception("Define property 'mime_type' before.")
        return Publisher(cls.get_connector(), cls.mime_type)

    @classmethod
    def deserialize_message(cls, mq_message):
        if cls.mime_type is NotImplemented:
            raise Exception("Define property 'mime_type' before.")
        return cls.mime_type.deserializer(mq_message)

    def consume(self, consumers_cnt: int = 1):
        consumers_list = []
        runnable = self.consumer.run
        if consumers_cnt == 1:
            runnable()
        else:
            for i in range(consumers_cnt):
                p = multiprocessing.Process(target=runnable)
                consumers_list.append(p)
                p.start()
