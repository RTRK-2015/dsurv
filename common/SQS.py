import boto3


# Class that provides a more high-level interface to SQS.
class SQS:
    # Constructs a new queue or opens the existing one if it exists.
    def __init__(self, name):
        self.client = boto3.client("sqs")
        response = self.client.list_queues(
            QueueNamePrefix=name
        )

        if "QueueUrls" not in response:
            response = self.client.create_queue(
                QueueName=name
            )
            self.url = response["QueueUrl"]
        else:
            self.url = response["QueueUrls"][0]

    def __enter__(self):
        return self

    # Deletes the queue.
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.delete_queue(
            QueueUrl=self.url
        )

    # Sends a message to the queue.
    def send(self, msg, attrs):
        self.client.send_message(
            QueueUrl=self.url,
            MessageBody=msg,
            MessageAttributes=attrs,
            DelaySeconds=0
        )

    # Gets a single message from the queue, or None, if there are no messages.
    def recv(self):
        response = self.client.receive_message(
            QueueUrl=self.url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=["All"]
        )

        if "Messages" not in response:
            return None

        messages = response["Messages"]
        message = messages[0]

        self.client.delete_message(
            QueueUrl=self.url,
            ReceiptHandle=message["ReceiptHandle"]
        )

        return message
