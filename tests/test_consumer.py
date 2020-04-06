from mq_consumer.connectors import Connector
from mq_consumer.consumers import NotEmptyConsumer
from mq_consumer.convenience import BaseConsumer
from mq_consumer.mime_types import MqMimeTypesEnum

from tests.test_connection_params import connection_parameters


class TestConsumer(BaseConsumer):
    consumer_type = NotEmptyConsumer
    connector_type = Connector

    connection_params = connection_parameters

    exchange = 'exchange'
    exchange_type = 'direct'
    routing_key = None
    queue = 'test'

    mime_type = MqMimeTypesEnum.pickle

    def __init__(self):
        super().__init__(finish_handler=lambda: print("FINISHED"))

    def handle(self, channel, method, properties, body):
        print(self.deserialize_message(body))
        channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    TestConsumer().consume()
