import json
from enum import Enum


class ResponseError(Enum):
    BOTH = 0
    NONE = 1


class Responses:
    @staticmethod
    def encode_success(s3url):
        return json.dumps({
            "s3url": s3url
        })

    @staticmethod
    def encode_fail(err_msg):
        return json.dumps({
            "error": err_msg
        })

    @staticmethod
    def decode(json_text):
        value_dict = json.loads(json_text)
        is_s3url = "s3url" in value_dict
        is_error = "error" in value_dict
        if is_error == is_s3url:
            if is_error:
                error_type = ResponseError.BOTH
            else:
                error_type = ResponseError.NONE

            raise ResponseDecodeError(error_type)

        return value_dict


class ResponseDecodeError(BaseException):
    def __init__(self, res_err):
        if res_err == ResponseError.BOTH:
            self.message = "Too many keys in response"
        elif res_err == ResponseError.NONE:
            self.message = "Too few keys in response"
