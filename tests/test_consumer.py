from mq_consumer.connectors import Reconnector
from mq_consumer.consumers import SafeConsumer

from tests.test_connection_params import connection_parameters


class TestConsumer(SafeConsumer):
    def __init__(self):
        connector = Reconnector(
            connection_parameters,
            'exchange',
            'test',
        )
        super().__init__(connector, self.handle)

    @staticmethod
    def handle(channel, method, properties, body):
        print(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)


def run():
    TestConsumer().run()


if __name__ == '__main__':
    run()
