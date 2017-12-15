import json


class Requests:
    @staticmethod
    def encode_direct(text, queue_name, words=None):
        return json.dumps({
            "text": text,
            "words": words,
            "queue_name": queue_name
        })

    @staticmethod
    def decode_direct(json_text):
        value_dict = json.loads(json_text)
        for key in ["text", "words", "queue_name"]:
            if key not in value_dict:
                raise RequestDecodeError(key)

        return value_dict

    @staticmethod
    def encode_file(url, queue_name, words=None):
        return json.dumps({
            "url": url,
            "words": words,
            "queue_name": queue_name
        })

    @staticmethod
    def decode_file(json_text):
        value_dict = json.loads(json_text)
        for key in ["url", "words", "queue_name"]:
            if key not in value_dict:
                raise RequestDecodeError(key)

        return value_dict


class RequestDecodeError(BaseException):
    def __init__(self, field):
        self.message = "Field {} does not exist".format(field)
