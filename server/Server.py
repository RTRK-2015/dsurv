import json
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


class S3Deleter:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        S3.destroy(self.bucket_name)


# A helper function to delay deletion of output bucket by 10 minutes.
def delayed_delete(bucket_name):
    with S3Deleter(bucket_name):
        time.sleep(10 * 60)


# Helper function to send an error to the client if something went wrong.
def send_error(queue_name):
    try:
        sqs = SQS(queue_name)
        sqs.send(
            msg=Responses.encode_fail("Shit hit the fan"),
            attrs={}
        )
    except BaseException as e:
        print("Well, that went really wrong: {}".format(e))


# Helper function to download and read data from the input bucket.
def get_bucket_file_data(in_bucket_name, remote_file):
    local_file = str(uuid.uuid4())

    try:
        bucket = S3(in_bucket_name)
        bucket.download(
            local_file=local_file,
            remote_file=remote_file
        )

        with open(local_file) as f:
            text = f.read()
        return text
    finally:
        os.remove(local_file)


# Function that counts all words
def process_all(words):
    result = {}

    for word in words:
        if word not in result:
            result[word] = 1
        else:
            result[word] += 1

    return result


# Function that counts only the words given by `check_words'.
def process_certain(words, check_words):
    result = {}

    for word in check_words:
        result[word] = sum(1 if w == word else 0 for w in words)

    return result


# Function that unifies two types of word processing.
def process(text, check_words):
    words = text.split()
    words = list(map(lambda word: re.sub("[^A-Za-z']", lambda _: "", word), words))

    # If there were no given words to count, just count them all
    if check_words is None:
        return process_all(words)
    # If the given words are actually an empty list, just return an empty object
    elif len(check_words) == 0:
        return {}
    # Otherwise, count only the given words
    else:
        return process_certain(words, check_words)


# A helper function to respond successfully to the request. It uploads the
# result file to a bucket and sends a message to the client.
def respond_success(queue_name, local_file):
    bucket_name = "titos-{}".format(str(uuid.uuid4()))
    bucket = S3(bucket_name)
    bucket.upload(
        local_file=local_file,
        remote_file="a.txt"
    )
    os.remove(local_file)
    SQS(queue_name).send(
        msg=Responses.encode_success("{} a.txt".format(bucket_name)),
        attrs={}
    )
    Process(
        target=delayed_delete,
        args=(bucket_name,)
    ).start()


# Unified handler, works with pure text
def handle(text, words, queue_name):
    processed = process(text, words)
    local_file = str(uuid.uuid4())
    with open(local_file, "w") as f:
        f.write(json.dumps(processed))
    respond_success(queue_name, local_file)


# Handles both request types by unifying them to a single request type.
def handle_json_request(msg, in_bucket_name):
    queue_name = "whoops"

    try:
        req = Requests.decode(msg)
        words = req["words"]
        queue_name = req["queue_name"]

        # If the request was of the "text" type, simply read the text from the request
        if "text" in req:
            print("Handling direct request: {}".format(req))
            text = req["text"]
        # If the request was of the "url" type, use a helper function to read the text from the bucket.
        elif "url" in req:
            print("Handling file request: {}".format(req))
            text = get_bucket_file_data(in_bucket_name, req["url"])
        else:
            print("Valid, yet invalid request: {}".format(req))
            raise RuntimeError("Valid, yet invalid request")

        # Delegate to unified handler
        handle(text, words, queue_name)
    except ValueError as e:
        print("Ignoring invalid json: {}\n{}".format(msg, e))
        send_error(queue_name)
    except DecodeError as e:
        print("Ignoring invalid request: {}\n{}".format(msg, e))
        send_error(queue_name)
    except BaseException as e:
        print("Ignoring exception: {}\n".format(e))
        send_error(queue_name)


class Server:
    def __init__(self, queue_name, bucket_name):
        self.queue = SQS(queue_name)
        self.bucket_name = bucket_name
        self.bucket = S3(bucket_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bucket.__exit__(exc_type, exc_val, exc_tb)
        self.queue.__exit__(exc_type, exc_val, exc_tb)

    # Main "entry" point for server. Starts the infinite loop for message processing.
    def run(self):
        print("Receiving and handling messages")
        while True:
            self.receive_and_handle()

    # Function that receives a message and starts a new process to handle the request
    def receive_and_handle(self):
        try:
            msg = self.queue.recv()
            if msg is None:
                time.sleep(0.005)
            else:
                print("Got message: \t{}".format(msg))
                Process(
                    target=handle_json_request,
                    args=(msg["Body"], self.bucket_name)
                ).start()
        except BaseException as e:
            print("Ignoring exception {}\n".format(e))


