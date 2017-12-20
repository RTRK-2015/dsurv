import unittest
import time
import os
import json
import uuid
from argparse import ArgumentParser

from common.Requests import Requests
from common.Responses import Responses
from common.S3 import S3
from common.SQS import SQS


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        "-q",
        "--queue",
        help="Server queue name",
        default="server-input"
    )

    parser.add_argument(
        "-b",
        "--bucket",
        help="Server input bucket",
        default="titos-treasury-1"
    )

    return parser.parse_args()


my_queue_name_prefix = "test-server-functionality-"
no_queue_name_prefix = "non-existing-"


class TestServerFunctionality(unittest.TestCase):
    def send_direct(self, data, really):
        my_queue_name = my_queue_name_prefix + str(uuid.uuid4())
        no_queue_name = no_queue_name_prefix + str(uuid.uuid4())

        with SQS(my_queue_name) as my_queue:
            sqs = SQS(args.queue)
            sqs.send(
                msg=Requests.encode_direct(data, my_queue_name if really else no_queue_name),
                attrs={}
            )

            count = 0
            msg = {}
            while count < 100:
                msg = my_queue.recv()
                if msg is None:
                    time.sleep(0.005)
                    count += 1
                else:
                    break
            else:
                if really:
                    self.fail("No response from the server")
                else:
                    return

            res = Responses.decode(msg["Body"])
            self.assertTrue("error" not in res)
            self.assertTrue("s3url" in res)
            parts = res["s3url"].split()
            self.assertEqual(len(parts), 2)
            bucket = parts[0]
            name = parts[1]

            res_s3 = S3(bucket)
            local_file = "downloaded.txt"
            res_s3.download(
                local_file=local_file,
                remote_file=name
            )
            data = ""
            with open(local_file, "r") as f:
                data = f.read()
            decoded = json.loads(data)
            os.remove(local_file)
            return decoded

    def send_file(self, name, really):
        my_queue_name = my_queue_name_prefix + str(uuid.uuid4())
        with SQS(my_queue_name) as my_queue:
            remote_file_name = my_queue_name + "-normal-file.txt"
            if really:
                with S3(args.bucket) as s3:
                    s3.upload(
                        local_file=name,
                        remote_file=remote_file_name
                    )

            sqs = SQS(args.queue)
            sqs.send(
                msg=Requests.encode_file(remote_file_name, my_queue_name),
                attrs={}
            )

            count = 0
            msg = {}
            while count < 100:
                msg = my_queue.recv()
                if msg is None:
                    time.sleep(0.005)
                    count += 1
                else:
                    break
            else:
                self.fail("No response from the server")

            res = Responses.decode(msg["Body"])
            if really:
                self.assertTrue("error" not in res)
                self.assertTrue("s3url" in res)
                parts = res["s3url"].split()
                self.assertEqual(len(parts), 2)
                bucket = parts[0]
                name = parts[1]

                res_s3 = S3(bucket)
                local_file = "{}-downloaded.txt".format(name)
                res_s3.download(
                    local_file=local_file,
                    remote_file=name
                )
                data = ""
                with open(local_file, "r") as f:
                    data = f.read()
                decoded = json.loads(data)
                os.remove(local_file)
                return decoded
            else:
                self.assertTrue("error" in res)
                self.assertTrue("s3url" not in res)

    def test_normal_file(self):
        print("Testing normal file")
        decoded = self.send_file("lorem.txt", True)
        self.assertEqual(decoded["sed"], 185)

    def test_normal_direct(self):
        print("Testing normal direct")
        with open("lorem.txt", "r") as f:
            data = f.read()
            decoded = self.send_direct(data, True)
            self.assertEqual(decoded["sed"], 185)

    def test_empty_file(self):
        print("Testing empty file")
        decoded = self.send_file("empty.txt", True)
        self.assertEqual(len(decoded), 0)

    def test_empty_direct(self):
        print("Testing empty direct")
        decoded = self.send_direct("", True)
        self.assertEqual(len(decoded), 0)

    def test_no_file(self):
        print("Testing no file")
        self.send_file("blah.txt", False)

    def test_no_queue(self):
        print("Testing no queue")
        self.send_direct("lorem.txt", False)


args = {}

if __name__ == '__main__':
    args = parse_args()
    unittest.main()
