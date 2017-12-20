import unittest

from client.Client import Client
from common.Requests import Requests
from common.Responses import Responses
from common.S3 import S3
from common.SQS import SQS

test_in_b = "test-input-bucket-1234"
test_out_b = "test-output-bucket-1234"

test_req_q = "test-request-queue"
test_res_q = "test-response-queue"

test_in_file = "lorem.txt"


class TestClientCase(unittest.TestCase):

    def set_up_req(self, req_q_name, in_b_name, res_q_name):
        self.cli = Client(res_q_name, req_q_name, in_b_name)
        self.in_b = S3(in_b_name)
        #self.out_b = S3(test_out_b)
        self.req_q = SQS(req_q_name)

    def tear_down_req(self):
        exc_type = None
        exc_val = None
        exc_tb = None
        self.cli.__exit__(exc_type, exc_val, exc_tb)
        self.req_q.__exit__(exc_type, exc_val, exc_tb)
        self.in_b.__exit__(exc_type, exc_val, exc_tb)
        #self.out_b.__exit__(exc_type, exc_val, exc_tb)

    def recv_req(self):
        count = 0
        while count < 20:
            msg = self.req_q.recv()

            if msg is None:
                count += 1
                continue

            return Requests.decode(msg["Body"])

        else:
            self.fail("Did not receive request")

    def test_file_req(self):
        self.set_up_req("test_file_req_q", "test_file_in_b", "test_file_res_q")
        self.cli.request(
            is_file=True,
            words=None,
            input_file=test_in_file
        )

        req = self.recv_req()

        for key in ["url", "words", "queue_name"]:
            if key not in req:
                self.fail("Invalid request")

        self.in_b.download(req["url"], req["url"])

        self.tear_down_req()

    def xtest_direct_req(self):
        self.cli.request(
            is_file=False,
            words=None,
            input_file=test_in_file
        )

        req = self.recv_req()

        for key in ["text", "words", "queue_name"]:
            if key not in req:
                self.fail("Invalid request")

    def xtest_response(self):
        # self.out_b.upload("lorem.txt", "a.txt")
        # Responses.encode_success("{} a.txt".format(test_out_b))
        # res = self.cli.wait_response()
        pass

    def xtest_get_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
