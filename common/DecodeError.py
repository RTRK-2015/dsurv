from enum import Enum


class KeyErrorEnum(Enum):
    TOO_MANY = 0
    TOO_FEW = 1


class DecodeError(BaseException):
    def __init__(self, res_err):
        if res_err == KeyErrorEnum.TOO_MANY:
            self.message = "Too many keys in response"
        elif res_err == KeyErrorEnum.TOO_FEW:
            self.message = "Too few keys in response"
