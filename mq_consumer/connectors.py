import pika
import pika.credentials
import pika.exceptions


class Connector:
    DELAY_TYPE = 'x-delayed-message'
    DIRECT_TYPE = 'direct'

    def __init__(self,
                 connection_parameters: pika.ConnectionParameters,
                 exchange: str,
                 queue: str,
                 routing_key: str = None,
                 prefetch_count: int = 1,
                 use_delay: bool = False):
        self.connection_parameters = connection_parameters
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key or queue
        self.prefetch_count = prefetch_count
        self.connection = None
        self.channel = None
        self.declared_queue = None
        self.use_delay = use_delay
        if self.use_delay:
            self.exchange_type = self.DELAY_TYPE
        else:
            self.exchange_type = self.DIRECT_TYPE
        self.create_connection()

    def create_connection(self):
        self.connection = pika.BlockingConnection(self.connection_parameters)
        self.channel = self.connection.channel()
        self.declared_queue = self.channel.queue_declare(queue=self.queue, durable=True)
        if self.use_delay:
            arguments = {"x-delayed-type": self.DIRECT_TYPE}
        else:
            arguments = None
        self.channel.exchange_declare(
            exchange=self.exchange, exchange_type=self.exchange_type, durable=True, arguments=arguments
        )
        self.channel.queue_bind(self.queue, self.exchange, routing_key=self.routing_key)
        if self.prefetch_count:
            self.channel.basic_qos(prefetch_count=self.prefetch_count)

    def close(self):
        if self.connection:
            self.connection.close()


class Reconnector(Connector):
    def __init__(self, connection_parameters: pika.ConnectionParameters, *args, **kwargs):
        connection_parameters.connection_attempts = float('inf')
        super().__init__(connection_parameters, *args, **kwargs)
