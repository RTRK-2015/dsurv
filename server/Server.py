import time
import uuid
import os
import re
from multiprocessing import Process

from common.Responses import Responses
from common.DecodeError import DecodeError
from common.Requests import Requests
from common.S3 import S3
from common.SQS import SQS


def get_bucket_file_data(in_bucket_name, remote_file):
    bucket = S3(in_bucket_name)
    local_file = str(uuid.uuid4())
    bucket.download(
        local_file=local_file,
        remote_file=remote_file
    )
    with open(local_file) as f:
        text = f.read()
        os.remove(local_file)
        return text


def process_all(words):
    result = {}

    for word in words:
        result[word] += 1

    return result


def process_certain(words, check_words):
    result = {}

    for word in check_words:
        result[word] = sum(1 if w == word else 0 for w in words)

    return result


def process(text, check_words):
    words = text.split()
    words.map(lambda word: re.sub("[^A-Za-z']", lambda _: "", word))

    if check_words is None:
        process_all(words)
    elif len(check_words) == 0:
        return {}
    else:
        process_certain(words, check_words)


def respond_error(queue_name):
    SQS(queue_name).send(
        msg=Responses.encode_fail("I sense a disturbance in the Force"),
        attrs={}
    )


def respond_success(queue_name, local_file):
    bucket_name = "titos-{}".format(str(uuid.uuid4()))
    bucket = S3(bucket_name)
    bucket.upload(
        local_file=local_file,
        remote_file="a.txt"
    )
    SQS(queue_name).send(
        msg=Responses.encode_success("{} a.txt".format(bucket_name)),
        attrs={}
    )


def handle(text, words, queue_name):
    local_file = str(uuid.uuid4())
    with open(local_file) as f:
        processed = process(text, words)
        if processed is None:
            respond_error(queue_name)
        else:
            respond_success(queue_name, local_file)
        os.remove(local_file)


def handle_json_request(msg, in_bucket_name):
    req = Requests.decode(msg)

    if "text" in req:
        print("Handling direct request: {}".format(req))
        text = req["text"]
    elif "url" in req:
        print("Handling file request: {}".format(req))
        text = get_bucket_file_data(in_bucket_name, req["url"])
    else:
        print("Valid, yet invalid request: {}".format(req))
        raise RuntimeError("Valid, yet invalid request")

    words = req["words"]
    queue_name = req["queue_name"]

    handle(text, words, queue_name)


class Server:
    def __init__(self, queue_name, bucket_name):
        self.queue = SQS(queue_name)
        self.bucket_name = bucket_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bucket.__exit__(exc_type, exc_val, exc_tb)
        self.queue.__exit__(exc_type, exc_val, exc_tb)

    def run(self):
        while True:
            self.receive_and_handle()

    def receive_and_handle(self):
        msg = self.queue.recv()
        try:
            if msg is None:
                time.sleep(0.005)
            else:
                Process(
                    target=handle_json_request,
                    args=(msg, self.bucket_name)
                ).start()
        except ValueError:
            print("Ignoring invalid json: {}".format(msg))
        except DecodeError:
            print("Ignoring invalid request: {}".format(msg))

