import time

from common.Requests import Requests
from common.Responses import Responses
from common.S3 import S3
from common.SQS import SQS


class Client:

    def __init__(self, cli_q_name, srv_q_name, srv_b_name):
        self.srv_q = SQS(srv_q_name)
        self.srv_b = S3(srv_b_name)
        self.cli_q = SQS(cli_q_name)
        self.cli_q_name = cli_q_name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cli_q.__exit__(exc_type, exc_val, exc_tb)

    def run(self, is_file, words, input_file, output_file):
        #send the request
        print("Sending request")
        self.request(
            input_file=input_file,
            is_file=is_file,
            words=words
        )

        #wait for the response
        #TODO: add timeout
        print("Waiting for response")
        res = self.wait_response()

        #get the file
        print("Getting file")
        self.get_file(res["s3url"], output_file)

    def request(self, is_file, words, input_file):
        #2 types of requests
        if is_file:
            #"file" request
            remote_file = self.cli_q_name + input_file
            self.srv_b.upload(
                local_file=input_file,
                remote_file=remote_file
            )
            #TODO: add waiter
            req = Requests.encode_file(
                queue_name=self.cli_q_name,
                words=words,
                url=remote_file
            )
        else:
            #"direct" request
            with open(input_file, "r") as f:
                text = f.read()

            req = Requests.encode_direct(
                queue_name=self.cli_q_name,
                words=words,
                text=text
            )

        self.srv_q.send(req, {})

    def wait_response(self):
        #straightforward blocking wait on response
        count = 0
        while True:
            res = self.cli_q.recv()

            #print(count)
            if count > 100:
                raise Exception("waiting for a response timed out")

            if res is None:
                count += 1
                time.sleep(0.006)
                continue

            dec = Responses.decode(res["Body"])

            if "error" in dec:
                raise Exception(dec["error"])

            return dec

    def get_file(self, s3url, output_file):
        #s3url has the following format:
        # "output_bucket_name output_file"
        #so we split them and use the names for the corresponding entities
        splits = s3url.split()
        out_b_name = splits[0]
        out_f = splits[1]

        out_b = S3(out_b_name)
        out_b.download(
            remote_file=out_f,
            local_file=output_file
        )
