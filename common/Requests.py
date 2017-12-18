import json

from common import *


class Requests:
    @staticmethod
    def encode_direct(text, queue_name, words=None):
        return json.dumps({
            "text": text,
            "words": words,
            "queue_name": queue_name
        })

    @staticmethod
    def encode_file(url, queue_name, words=None):
        return json.dumps({
            "url": url,
            "words": words,
            "queue_name": queue_name
        })

    @staticmethod
    def decode(json_text):
        value_dict = json.loads(json_text)

        is_text = "text" in value_dict
        is_url = "url" in value_dict
        if is_text == is_url:
            if is_text:
                error_type = KeyErrorEnum.TOO_MANY
            else:
                error_type = KeyErrorEnum.TOO_FEW

            raise RequestDecodeError(error_type)

        for key in ["words", "queue_name"]:
            if key not in value_dict:
                raise RequestDecodeError(KeyErrorEnum.TOO_FEW)

        return value_dict


class RequestDecodeError(DecodeError):
    def __init__(self, key_err_enum):
        super(key_err_enum)
