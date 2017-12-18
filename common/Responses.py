import json


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
                error_type = KeyErrorEnum.TOO_MANY
            else:
                error_type = KeyErrorEnum.TOO_FEW

            raise ResponseDecodeError(error_type)

        return value_dict


class ResponseDecodeError(DecodeError):
    def __init__(self, key_err_enum):
        super(key_err_enum)
