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

g_count = 0


class TestClientCase(unittest.TestCase):

    #standard setUp function to create instances of resources
    # that test cases will use
    def setUp(self):
        global g_count
        self.count = g_count
        g_count += 1

        self.req_q = SQS("{}-{}".format(test_req_q, self.count))
        self.in_b = S3("{}-{}".format(test_in_b, self.count))
        self.out_b = S3("{}-{}".format(test_out_b, self.count))
        self.cli = Client(
            "{}-{}".format(test_res_q, self.count),
            "{}-{}".format(test_req_q, self.count),
            "{}-{}".format(test_in_b, self.count)
        )

    #standard tearDown function to clean up the resources created in setUp
    def tearDown(self):
        exc_type = None
        exc_val = None
        exc_tb = None
        self.cli.__exit__(exc_type, exc_val, exc_tb)
        self.req_q.__exit__(exc_type, exc_val, exc_tb)
        self.in_b.__exit__(exc_type, exc_val, exc_tb)
        self.out_b.__exit__(exc_type, exc_val, exc_tb)

    #helper function for receiving a message from the request queue
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

    #Test case which tests whether or not a file request was completed successfully
    #tests the @Client @request method
    def test_file_req(self):
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

    #Test case which tests whether or not a direct request was completed successfully
    #tests the @Client @request method
    def test_direct_req(self):
        self.cli.request(
            is_file=False,
            words=None,
            input_file=test_in_file
        )

        req = self.recv_req()

        for key in ["text", "words", "queue_name"]:
            if key not in req:
                self.fail("Invalid request")

    #Tests a successful response reception
    #tests the Client <wait_response> method
    def test_response(self):
        #self.out_b.upload("lorem.txt", "a.txt")
        res = Responses.encode_success("{} a.txt".format(self.out_b.name))
        res_q = SQS(self.cli.cli_q_name)
        res_q.send(res, {})
        res = self.cli.wait_response()

    #Tests a successful error response reception
    #tests the @Client @wait_response method
    def test_response_error(self):
        res = Responses.encode_fail("Test error")
        res_q = SQS(self.cli.cli_q_name)
        res_q.send(res, {})

        with self.assertRaises(Exception):
            self.cli.wait_response()

    #Tests an unsuccessful response reception
    #tests the @Client @wait_response method
    def test_no_response(self):
        with self.assertRaises(Exception):
            self.cli.wait_response()

    #Tests a successful reception of the output file
    #test the @Client @get_file method
    def test_get_file(self):
        self.out_b.upload("{}".format(test_in_file), "a.txt")

        self.cli.get_file("{} {}".format(self.out_b.name, "a.txt"))

    #Tests an unsuccessful reception of the output file
    #tests the @Client @get_file method
    def test_get_no_file(self):
        with self.assertRaises(Exception):
            self.cli.get_file("{} {}".format(self.out_b.name, "a.txt"))

    def xtest_run(self):
        #TODO: implement? other methods all tested, redundant
        #"Mock" server run
        #New Process client.run
        pass


if __name__ == '__main__':
    unittest.main()
