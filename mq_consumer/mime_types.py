import json
import pickle
from enum import Enum
from typing import Callable

from mq_consumer.encoders import DateTimeDecimalJSONEncoder


class MqMimeTypesEnum(Enum):
    json = 'application/json'
    pickle = 'application/x-python-pickle'

    @property
    def serializer(self) -> Callable:
        if self == MqMimeTypesEnum.json:
            return lambda d: json.dumps(d, cls=DateTimeDecimalJSONEncoder)
        elif self == MqMimeTypesEnum.pickle:
            return pickle.dumps
        else:
            raise Exception("Unreachable statement")

    @property
    def deserializer(self) -> Callable:
        if self == MqMimeTypesEnum.json:
            return json.loads
        elif self == MqMimeTypesEnum.pickle:
            return pickle.loads
        else:
            raise Exception("Unreachable statement")
