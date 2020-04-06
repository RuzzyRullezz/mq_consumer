import json
import logging
import pickle

import pika
import pika.exceptions

from .connectors import Connector, Reconnector
from .mime_types import MqMimeTypesEnum


class Publisher:
    def __init__(self, connector: Connector, mime_type: MqMimeTypesEnum):
        self.connector = connector
        self.mime_type = mime_type
        self.connector.create_connection()

    def publish(self, **params):
        self.connector.channel.basic_publish(**params)

    def send_message(self, obj, content_type='text/plain', delay=0, properties=None):
        message = self.mime_type.serializer(obj)
        properties = properties or {}
        properties.update({
            'delivery_mode': 2,
            'content_type': content_type
        })
        if delay != 0:
            assert self.connector.use_delay, u'Publisher must have delay support'
            properties.update({
                'headers': {
                    'x-delay': delay
                }
            })
        params = {
            "exchange": self.connector.exchange,
            "routing_key": self.connector.routing_key,
            "body": message,
            "properties": pika.BasicProperties(**properties)
        }
        self.publish(**params)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connector.close()


class ReconPublisher(Publisher):
    def __init__(self, connector: Reconnector, mime_type: MqMimeTypesEnum, logger: logging.Logger = None):
        assert isinstance(connector, Reconnector), 'connector must be Reconnector instance'
        self.logger = logger
        super().__init__(connector, mime_type)

    def publish(self, **params):
        while True:
            try:
                super(ReconPublisher, self).publish(**params)
                break
            except pika.exceptions.AMQPError:
                if self.logger:
                    self.logger.exception('RabbitMQ publisher exception')
                self.connector.create_connection()
