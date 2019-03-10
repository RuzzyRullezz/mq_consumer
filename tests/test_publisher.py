import datetime

from tests.test_consumer import TestConsumer


def run():
    with TestConsumer().get_json_publisher() as test_publisher:
        test_publisher.send_message(dict(
            text='Сообщение',
            timestamp=datetime.datetime.now(),
        ))


if __name__ == '__main__':
    run()
